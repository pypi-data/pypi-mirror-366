import torch, math

from loguru import logger

from syndrilla.utils import dataset


class create():
    """
    This class creates a bsc error model.
    """
    def __init__(self, 
                 error_model_cfg, 
                 **kwargs) -> None:
        assert 'rate' in error_model_cfg.keys(), logger.error(f'Missing key <rate> in the configuration.')
        self.rate = error_model_cfg['rate']
        self.device = error_model_cfg['device']


    def inject_error(self, codeword, batch_size:int=0):
        logger.info(f'Injecting error.')

        codeword = codeword.to(self.device)
        if batch_size == 0:
            batch_size = codeword.size(0)
        # random values in [0,1)
        random_values = torch.rand_like(codeword)
        self.dtype = codeword.dtype
        self.len = codeword.shape
        
        error = torch.where(random_values < self.rate, 1 - codeword, codeword)
        dataloader = torch.utils.data.DataLoader(dataset(error, self.get_llr(), torch.arange(0, codeword.size(0))), batch_size=batch_size, shuffle=False)
        logger.info(f'Injection complete.')
        return error, dataloader
    

    def get_llr(self):
        llr =  torch.full(self.len, math.log((1 - self.rate)/self.rate), device=self.device, dtype=self.dtype)
        return llr
    
