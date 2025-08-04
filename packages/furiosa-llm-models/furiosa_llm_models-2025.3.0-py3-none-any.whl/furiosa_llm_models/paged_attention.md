# Paged Attention model modification

이 문서의 목적은 paged attention 을 레니게이드에 적용하기 위해 어떤 변환들이 필요한지를 서술하는 것을 목적으로 합니다. 

## Paged Attention 의 아이디어

paged attention의 아이디어는 간단합니다. sequence 의 token 들에 해당하는 kv cache 들을 하나의 전체 sequence 가 아닌 작은 단위의 block 으로 저장하는것을 골자로 합니다. 즉, cpu 와 비슷하게 gpu(npu)에서의 memory fragmentation의 최소화를 목표로 합니다.

예를 들어 sequence 가 다음과 같이 "A B C D E F"(6 tokens) 이라면 기존의 방식에서는 6 tokens 전체를 한번에 저장을 하는 방식이었는데 block(ex: 2 tokens per block)단위로 저장을 하게 되면
["A B", "C D", "E F"] 처럼 각각의 block의 크기를 작게해서 저장을 할수 있습니다. 
이후 kv cache 를 가져와서 연산을 수행할때는 block 들의 index(즉, 각 block들이 저장되어 있는 memory address)를 통해 "A B C D E F" 만큼의 kv cache 를 다시 reconstruct 해서 연산을 수행하면 됩니다. 
그 후 새로 생성된 kv cache 는 원래 가야 하는 block의 위치에 넣어주면 됩니다. 즉, paged attention 을 적용한 모델의 작동 방식은 다음과 같이 정리할수 있습니다. 

0. 사용할수 있는 dram 영역을 block 의 크기에 맞게 미리 쪼개두기
1. 새로 생성된 kv cache 값을 runtime 이 지정한 위치(0에서 쪼개둔 block 중 어딘가)에 쓰기
2. 새로 생성된 kv cache 값을 비롯해 기존의 past kv cache 값을 gather 해서 attention 연산에 필요한 kv cache 만들기
3. attention 연산하기 

입니다.

이를 통해 얻을 수 있는 이점은 여러가지가 있는데 예를 들어 
1. batch 처리: batch로 sequence 들을 처리를 하게 되면 가장 긴 length 를 가진 sequence가 기준이 되어 나머지 sequence 들은 본인 length - padding 만큼 패딩을 하게 됩니다. 이 padding 들에 대한 kv cache 값도 저장을 하게 된다면 불필요한 메모리 낭비가 발생하게 됩니다. 
2. beam search: beam search 같이 같은 prompt들을 공유하는 sequence 들이 있을때 이 공통된 prompt에 해당하는 kv cache 를 한번의 저장으로 공유할수 있습니다. 

단점은
1. 위 단계에서 dram 여러 곳에 흩어진 past kv cache 를 가져오는 "gather" 가 추가적인 cost 를 야기할수 있습니다


## Block size

위 설명에서 하나의 block은 N token 들의 kv cache 를 저장할수 있는 조각이라고 정의를 했습니다. 여기서 N 은 hyperparameter 로 실험을 통해 최적의
값을 찾아야 합니다. N이 hyperparameter인 이유는 gpu 에서

1. If the block size is too small, vLLM may not fully utilize the GPU’s parallelism for reading and processing KV cache. 

2. If the block size is too large, internal fragmentation increases and the probability of sharing decreases

여기서 주의해야할 점은 block_size 가 작으면 fragmentation은 줄일수 있어서 좋은데 gpu의 parallelism을 충분히 활용하지 못하는 문제입니다. 

이는 paged attention 논문에서 하나의 kv cache block을 하나의 warp에서 연산을 처리하게 하는데 launch 될수있는 warp 의 수는 정해져 있어서 block이 많다고 이를 물리적으로 동시에 처리하기 어렵기 때문에 발생합니다. 다만 이는 현재 레니게이드에서 저희 컴파일러가 작동하는 방식과 달라서 우회가 가능합니다. 저희 컴파일러 입장에서는 각 block 들을 처리의 대상으로 보는게 아니라 attention 연산 전체(gather 한 block들)를 컴파일 대상으로 보기 때문에 이 constraint 가 저희에는 적용이 되지 않습니다. 

다만 gpu 에서도 떨어져 있는 주소들을 gather 하는건 추가 operation 이 필요한데 이는 renegade 에서도 유효한 constraint 입니다. 현재 renegade 에서는 dma 를 할때 4GB밖으로 떨어져 있지 않은 주소들에 대해서 indirect access를 통한 dma를 할수 있어서 block 들이 4GB 밖으로 떨어져 있지 않은지 확인해야 합니다. 이를 최대한 우회하기 위해 key, value 를 layer 마다 따로 저장하게 되면(layer 마다 연산은 별개이기 때문에) gptj(bf16) 기준 최대 524288개 정도의 token 들을 4GB 밖으로 안 벗어나게 유지할수 있어서 일반적인 use case(max sequence 를 가정한 상태에서 batch size = 256) 에서는 문제가 없습니다. 

즉, max_sequence = 2k, batch_size = 256 내에서는 token 들이 모두 한 번의 dma access 범위인 4GB에 들어오게 저장을 할수 있기 때문에 레니게이드에서 gather operation은 1의 access 로 가능해서 추가 cost는 없습니다. 그러므로 block_size=1 로 가져가는게 레니게이드에서 가능하고 성능 상의 cost는 거의 없을것으로 예상됩니다. 

## Inplace Mutation in torch model 

Note: torch로 작성된 model에서 input/output tensor를 제외한 모든 tensor(중간 연산에 쓰이는 tensor 포함)은 logical하게 존재하는것은 맞지만 실제로 dram에 저장(할당)이 되는것을 보장하지 않습니다. 

위에서 설명한 로직을 간단한 코드로 표현을 하자면 

```py

def attn(self, hidden_states, attention_mask, total, new_key_location, new_value_location, all_key_location, all_value_location):
    query = self.q_proj(hidden_states)
    new_key = self.k_proj(hidden_states)
    new_value = self.v_proj(hidden_states)

    def reshape_and_cache(total, new_key, new_value, new_key_location, new_value_location)
        """
        An abstract class to handle weights initialization and a simple interface for downloading and loading pretrained models.
        """  
        total[new_key_location] = new_key
        total[new_value_location] = new_value
    
    def gather(total, all_key_location, all_value_location):
        # below indexing will be understood as aten.index_select which would be scatter_read in renegade
        return (total[all_key_location], total[all_value_location])

    reshape_and_cache(total, new_key, new_value, new_key_location, new_value_location)
    gathered_key, gathered_value = gather(total, all_key_location, all_value_location)

    # do actual attention
    
    self._attn(query, gatherd_key, gathered_value, attention_mask, ...)
    return
```

로 설명할수 있습니다.
