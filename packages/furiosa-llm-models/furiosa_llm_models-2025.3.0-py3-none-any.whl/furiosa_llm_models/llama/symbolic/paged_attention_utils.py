import torch


def reshape_and_cache(
    target: torch.Tensor,
    total: torch.Tensor,
    new_target_location: torch.Tensor,
):
    indices = torch.squeeze(new_target_location.reshape(1, -1), dim=0)
    batch, seq, num_head, head_dim = target.shape
    total[indices] = target.reshape(batch * seq, 1, num_head, head_dim)
