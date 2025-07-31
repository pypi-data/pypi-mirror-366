# copyright ############################### #
# This file is part of the Xpart Package.   #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

import numpy as np
from scipy.constants import c
import scipy.special
import scipy.integrate as integrate
from scipy.special import gamma as Gamma

from ..general import _print


class SingleRFHarmonicMatcher:
    def __init__(self,
                 q0=None,
                 voltage=None,
                 length=None,
                 freq=None,
                 p0c=None,
                 slip_factor=None,
                 beta0=None,
                 rms_bunch_length=None, distribution="parabolic",
                 transformation_particles=400000, n_points_in_distribution=300,
                 verbose=0, m=4.7, q=1.0):

        self.verbose = verbose
        self.transformation_particles = transformation_particles

        self.length = length

        # Hamoltonian: H = A cos(B tau) - C ptau^2
        # normalized Hamiltonian: m = ( sin(B/2*tau) )^2 + C/(2A) ptau^ 2
        self.A = q0*voltage/(2.*np.pi*freq*p0c/c*length)
        self.B = 2*np.pi*freq/c
        self.C = abs(slip_factor)/(2.*beta0*beta0)
        # the difference between above and below transition is that the Hamiltonian flips sign
        # (considering always the absolute value of the slip factor)a. This is the same as if
        # the particle goes back in turns. For the purpose of matching, this is of no concern.

        tau_ufp = self.get_unstable_fixed_point()
        dtau = 0.01*tau_ufp # don't get too close to the separatrix
        tau_lim = tau_ufp - dtau
        self.tau_distr_x = np.linspace(- tau_lim, tau_lim, n_points_in_distribution)
        if distribution == "parabolic":
            tau_max = np.sqrt(5)*rms_bunch_length
            lambda_dist = lambda tau, tau_max: 1 - (tau/tau_max)**2
            # correct bunch length (due to truncation at separatrix)
            if tau_max > tau_lim:
                # analytical_tau_max = np.sqrt((5*tau_lim**3*rms_bunch_length**2 - 3*tau_lim**5)/(15*tau_lim*rms_bunch_length**2 - 5*tau_lim**3))
                func_to_solve = lambda new_tau_max: (scipy.integrate.quad(lambda x: (x**2 - rms_bunch_length**2)*lambda_dist(x, new_tau_max), -tau_lim, tau_lim))[0]
                corrected_tau_max = scipy.optimize.fsolve(func_to_solve, x0=tau_max)[0]
                tau_max = corrected_tau_max
            self.tau_distr_y = lambda_dist(self.tau_distr_x, tau_max)
            self.tau_distr_y[abs(self.tau_distr_x) > tau_max] = 0
            if tau_max >= tau_ufp:
                _print(f"WARNING SingleRFHarmonicMatcher: longitudinal profile larger than bucket, truncating to unstable fixed point. tau_max = {tau_max:.4f}, tau_ufp = {tau_ufp:.4f} ")

            _print(f"SingleRFHarmonicMatcher: Parabolic parameter is equal to {tau_max:.3f}m to achieve target RMS bunch length ({rms_bunch_length:.3f}m).")
        elif distribution == "gaussian":
            lambda_dist = lambda tau, rms: np.exp(-tau**2/2./rms**2)

            # correct bunch length (due to truncation at separatrix)
            func_to_solve = lambda new_rms: (scipy.integrate.quad(lambda x: (x**2 - rms_bunch_length**2)*lambda_dist(x, new_rms), -tau_lim, tau_lim))[0]
            corrected_rms = scipy.optimize.fsolve(func_to_solve, x0=rms_bunch_length)[0]

            _print(f"SingleRFHarmonicMatcher: Gaussian parameter is equal to {corrected_rms:.3f}m to achieve target RMS bunch length ({rms_bunch_length:.3f}m).")

            self.tau_distr_y = lambda_dist(self.tau_distr_x, corrected_rms)
        elif distribution == "qgaussian":
            # Q-Gaussian from Eq. (2.1) in (Umarov, Tsallis, Steinberg, 2008) 
            #available at https://link.springer.com/article/10.1007/s00032-008-0087-y
            if q>5./3.:
                q = 1.6 # slightly below defined region
                _print(f"WARNING SingleRFHarmonicMatcher: q-value above 5/3 undefined for correct RMS bunch length, truncating q value to {q:.3f}")
            beta = 1.0/(rms_bunch_length**2 * (5.-3.*q)) # solving from variance
            lambda_dist = lambda tau, beta: np.sqrt(beta) / self._Cq(q) * self._eq(-beta * tau**2, q)
            
            func_to_solve = lambda new_beta: (scipy.integrate.quad(lambda x: (x**2 - rms_bunch_length**2)*lambda_dist(x, new_beta), -tau_lim, tau_lim))[0]
            corrected_beta = scipy.optimize.fsolve(func_to_solve, x0=beta)[0]
            _print(f"SingleRFHarmonicMatcher: q-Gaussian parameter beta = {corrected_beta:.3f} for q={q:.3f} to achieve target RMS bunch length ({rms_bunch_length:.3f}m).")

            self.tau_distr_y = lambda_dist(self.tau_distr_x, corrected_beta)
            
        elif distribution == "binomial":
            # Binomial distribution adds tail to parabolic, see (Joho, 1980) at https://indico.psi.ch/event/3484/attachments/5948/7502/TM-11-14.pdf
            # behaviour is Gaussian for m --> inf
            tau_max = 1.0 # starting value, will be adjusted. Used as benchmarking value with RMS factor for parabola
            lambda_dist = lambda tau, tau_max: (1 - (tau/tau_max)**2)**(m-0.5) 
            binomial_2nd = lambda tau, tau_max: (1 - (tau/tau_max)**2)**(m-0.5)*tau**2
            RMS_binomial = np.sqrt(integrate.quad(binomial_2nd, -1, 1, args=(tau_max))[0] / integrate.quad(lambda_dist, -1, 1, args=(tau_max))[0])
            factor_binomial = tau_max / RMS_binomial
            _print(f"RMS factor for binimial is {factor_binomial:.3f}")
            tau_max = factor_binomial*rms_bunch_length 
            func_to_solve = lambda new_tau_max: (scipy.integrate.quad(lambda x: (x**2 - rms_bunch_length**2)*lambda_dist(x, new_tau_max), -tau_lim, tau_lim))[0]
            corrected_tau_max = scipy.optimize.fsolve(func_to_solve, x0=tau_max)[0]
            tau_max = corrected_tau_max
            self.tau_distr_y = lambda_dist(self.tau_distr_x, tau_max)
            self.tau_distr_y[abs(self.tau_distr_x) > tau_max] = 0
            _print(f"SingleRFHarmonicMatcher: Binomial x_lim parameter is equal to {tau_max:.3f}m to achieve target RMS bunch length ({rms_bunch_length:.3f}m).")
        else:
            raise NotImplementedError

        self.m_distr_x, self.m_distr_y = self.transform_tau_distr_to_m_distr()


    def transform_tau_distr_to_m_distr(self):
        xp = self.tau_distr_x.copy()
        yp = self.tau_distr_y.copy()
        N = int(len(xp)/2.)
        dx = xp[1] - xp[0]
        m_distr_x = []
        m_distr_y = []
        for ii in range(N):
            jj = len(xp) - ii - 1 #start from end
            tau = xp[jj]
            dens = yp[jj]
            if dens == 0.:
                continue
            if self.verbose:
                _print(f"tau = {tau:.3f}, f(tau) = {dens:.3f}")

            m0 = self.get_m(tau=tau - dx/2.)
            m1 = self.get_m(tau=tau + dx/2.)
            dm = m1 - m0
            m = self.get_m(tau=tau)
            if m == 1.0:
                continue
            _print('SingleRFHarmonicMatcher: Transforming distribution: '
                        f'{round(ii/N*100):2d}%  ',end="\r", flush=True)
            tau_test, ptau_test = self.get_airbag_from_m(m=m, n_particles=self.transformation_particles)
            hist, bin_edges = np.histogram(tau_test, bins=len(xp), range=(min(xp)-dx/2., max(xp)+dx/2.))

            hist = (hist + hist[::-1])/2.
            factor = dens/hist[jj]
            yp -= hist*factor
            m_distr_x.append(m)
            m_distr_y.append(np.sum(hist)*factor/dm)

        m_distr_x.append(0)
        m_distr_y.append(0)
        m_distr_x = m_distr_x[::-1]
        m_distr_y = m_distr_y[::-1]

        _print('SingleRFHarmonicMatcher: Done transforming distribution.')
        return m_distr_x, m_distr_y


    def get_separatrix(self):
        ufp = self.get_unstable_fixed_point()
        xx = np.linspace(-ufp, ufp, 1000)
        yy = np.sqrt(2*self.A/self.C) * np.cos(self.B/2.*xx)
        return xx, yy

    def get_unstable_fixed_point(self):
        return np.pi/self.B

    def get_m(self, tau=0, ptau=0):
        return ( np.sin(self.B/2. * tau) )**2 + self.C / 2. / self.A * (ptau ** 2)

    def get_airbag_from_m(self, m, n_particles=20000):
        if n_particles is None:
            n_particles = len(m)

        K = scipy.special.ellipk(m)
        G = 2.*K/np.pi
        theta = np.random.uniform(size=n_particles)*2.*np.pi
        sn, cn, dn, ph = scipy.special.ellipj(G*theta,m)

        tau = 2./self.B*np.arcsin(np.sqrt(m)*sn)
        ptau = np.sqrt(2*self.A*m/self.C)*cn

        return tau, ptau

    def sample_tau_ptau(self, n_particles=20000):
        max_m = max(self.m_distr_x)
        tau_new = []
        ptau_new = []
        counter = 0
        max_y = np.max(self.m_distr_y)
        chunk = 20000
        ### Acceptance-rejection algorithm sampling from distribution of m and a random "angle"
        ### The random angle is the conjugate variable to the action variable and is only
        ### approximately equal to the angle in the tau-ptau space.
        while counter < n_particles:
            m = np.random.random(size=chunk)*max_m
            rand_test = np.random.random(size=chunk)*max_y
            yy = np.interp(m, self.m_distr_x, self.m_distr_y)

            tau, ptau = self.get_airbag_from_m(m, n_particles=None)

            mask = rand_test < yy

            tau_new.extend(list(tau[mask]))
            ptau_new.extend(list(ptau[mask]))
            counter += sum(mask)
            _print('SingleRFHarmonicMatcher: Sampling particles: '
                        f'{round(counter/n_particles*100):2d}%  ',end="\r", flush=True)
        _print(f"SingleRFHarmonicMatcher: Sampled {n_particles} particles")

        return tau_new[:n_particles], ptau_new[:n_particles]

    def generate(self, n_particles=20000):
        tau, ptau = self.sample_tau_ptau(n_particles=n_particles)

    def get_synchrotron_tune(self):
        return self.B*np.sqrt(2*self.A*self.C)*self.length/(2*np.pi)

    def _Cq(self, q, margin=5e-4):
        """
        Normalization coefficient for Q-Gaussian
        
        Normalizing constant from Eq. (2.2) in https://link.springer.com/article/10.1007/s00032-008-0087-y
        with a small margin around 1.0 for numerical stability
        """
        if q < (1 - margin):
            Cq = (2 * np.sqrt(np.pi) * Gamma(1.0/(1.0-q))) / ((3.0 - q) * np.sqrt(1.0 - q) * Gamma( (3.0-q)/(2*(1.0 -q))))   
        elif (q > (1.0 - margin) and q < (1.0 + margin)):
            Cq = np.sqrt(np.pi)
        else:
            Cq = (np.sqrt(np.pi) * Gamma((3.0-q)/(2*(q-1.0)))) / (np.sqrt(q-1.0) * Gamma(1.0/(q-1.0)))
        if q > 3.0:
            raise ValueError("q must be smaller than 3!")
        else:
            return Cq
    
    
    def _eq(self, x, q):
        """ 
        Q-exponential function
        Available at https://link.springer.com/article/10.1007/s00032-008-0087-y
        """
        eq = np.zeros(len(x))
        for i, xx in enumerate(x):
            if ((q != 1) and (1 + (1 - q) * xx) > 0):
                eq[i] = (1 + (1 - q) * xx)**(1 / (1 - q))
            elif q==1:
                eq[i] = np.exp(xx)
            else:
                eq[i] = 0
        return eq
