# mlektic/linear_reg/linreg_utils_torch.py
import torch

def mse(y,t): return torch.mean((t-y)**2)
def rmse(y,t): return torch.sqrt(mse(y,t))
def mae(y,t): return torch.mean(torch.abs(t-y))
def mape(y,t): return torch.mean(torch.abs((t-y)/y))*100
def r2(y,t):
    ss_tot=torch.sum((y-y.mean())**2)
    ss_res=torch.sum((y-t)**2)
    return 1-ss_res/ss_tot
def corr(y,t):
    vx=y-y.mean(); vy=t-t.mean()
    return torch.sum(vx*vy)/(torch.sqrt(torch.sum(vx**2))*torch.sqrt(torch.sum(vy**2)))
