import numpy as np
from   scipy.stats import (multivariate_normal as mvn,
                           norm)
from   scipy.stats._multivariate import _squeeze_output
# import random

class multivariate_skewnorm:
    
    def __init__(self, shape, mean, cov=None):
        self.dim   = len(shape)
        self.shape = np.asarray(shape)
        self.mean  = np.asarray(mean)
        self.cov   = np.eye(self.dim) if cov is None else np.asarray(cov)

    def pdf(self, x):
        return np.exp(self.logpdf(x))
        
    def logpdf(self, x):
        x    = mvn._process_quantiles(x, self.dim)
        pdf  = mvn(self.mean, self.cov).logpdf(x)
        cdf  = norm(0, 1).logcdf(np.dot(x, self.shape))
        return _squeeze_output(np.log(2) + pdf + cdf)

    def rvs_slow(self, size=1):
        std_mvn = mvn(np.zeros(self.dim),
                    np.eye(self.dim))
        x       = np.empty((size, self.dim))
        
        # Apply rejection sampling.
        n_samples = 0
        while n_samples < size:
            z = std_mvn.rvs(size=1)
            u = np.random.uniform(0, 2*std_mvn.pdf(z))
            if not u > self.pdf(z):
                x[n_samples] = z
                n_samples += 1
        
        # Rescale based on correlation matrix.
        chol = np.linalg.cholesky(self.cov)
        x = (chol @ x.T).T
        return x

    def rvs(self, size=1):
        aCa      = self.shape @ self.cov @ self.shape
        delta    = (1 / np.sqrt(1 + aCa)) * self.cov @ self.shape
        cov_star = np.block([[np.ones(1),     delta],
                            [delta[:, None], self.cov]])
        x        = mvn(np.zeros(self.dim+1), cov_star).rvs(size)
        if size == 1:
            x0, x1 = x[0], x[1:]
        else: 
            x0, x1   = x[:, 0], x[:, 1:]
        inds     = x0 <= 0
        x1[inds] = -1 * x1[inds]
        return x1 + self.mean