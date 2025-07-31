import torch
import math

def orientLoss(input,target,dim=-1,meanOut=True,angleSmooth=1,normSmooth=1,dimScalingOrd=0,eps=1e-8):
    diff=input-target #注意这里顺序不要写反
    numel=diff.numel()
    MSE=torch.linalg.norm(diff,ord=2,dim=dim,keepdim=False)
    numel/=MSE.numel()
    t=target.broadcast_to(diff.size())
    TargetNorm=torch.linalg.norm(t,ord=2,dim=dim,keepdim=False)
    k=MSE*TargetNorm
    Dot=(diff*t).sum(dim=dim,keepdim=False)
    loss1=((1-Dot/(k+eps))/2).sqrt()**angleSmooth
    loss2=(k/(numel**dimScalingOrd))**normSmooth
    loss=loss1*loss2
    #loss[~torch.isfinite(loss)]=0
    
    if meanOut:
        return loss.mean()
    else:
        return loss
       
