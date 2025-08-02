from abc import ABC, abstractmethod, abstractproperty
import logging
logger = logging.getLogger('stan')
logger.addHandler(logging.NullHandler())
import stan #_jupyter as stan
import numpy as np
import concurrent.futures
import multiprocessing
multiprocessing.set_start_method('spawn', True)

# Renamed variables and methods to follow Python naming conventions (PEP8)
class MCDMProblem(ABC):
    _basic_model = ""
    _basic_model_clustering = ""
    _basic_model_sorting = ""
    
    _correlated_model = ""
    _correlated_model_clustering = ""
    _correlated_model_sorting = ""

    _is_correlated_model = False
    _is_clustering_required = False
    _is_sorting_required = False

    def __init__(self, alternatives, dm_cluster_number, alt_sort_number, num_chain, num_samples, options={}):
        self.alternatives = alternatives
        self.dm_cluster_number = dm_cluster_number
        self.alt_sort_number = alt_sort_number
        self.num_chains = num_chain
        self.num_samples = num_samples
        self.options = options

        if self.alternatives is not None or self.options.get('Sigma') is not None:
            self._is_correlated_model = True
        if self.options.get('CriteriaDependence') == False:
            self._is_correlated_model = False

        self._is_sorting_required = True if self.alt_sort_number > 0 else False
        self._is_clustering_required = True if self.dm_cluster_number > 0 else False

    @property
    def alt_no(self):
        return 0 if isinstance(self.alternatives, type(None)) else self.alternatives.shape[0]

    @abstractproperty
    def input_data(self):
        pass

    @abstractproperty
    def dm_no(self):
        pass
    
    @abstractproperty
    def criteria_no(self):
        pass
    
    @abstractmethod
    def _check_input_data(self):
        pass

    @property
    def model(self):
        model = 'self._'

        model = model + 'correlated_model' if self._is_correlated_model else model + 'basic_model'
        model = model + '_clustering' if self._is_clustering_required else model
        model = model + '_sorting' if self._is_sorting_required else model

        print("The used model is: ", model)
        return eval(model)

    def _get_common_data(self):
        data = {}
        data['gamma_param'] = 0.01
        data['sigma_coef'] = 0.1
        data['DmNo'] = self.dm_no
        data['CNo'] = self.criteria_no
        
        if self.dm_cluster_number > 0:
            data['DmC'] = self.dm_cluster_number

        if not isinstance(self.alternatives, type(None)):
            data['Alt'] = self.alternatives
            data['AltNo'] = self.alt_no

        if self.alt_sort_number > 0:
            data['AltC'] = self.alt_sort_number
            data['eAlt'] = np.ones(self.alt_sort_number)

        if self._is_correlated_model:
            data['mu'] = 0.01 * np.ones(self.criteria_no)
            data['Sigma'] = np.cov(self.alternatives.T)
            if not isinstance(self.options.get('Sigma'), type(None)):
                data['Sigma'] = self.options.get('Sigma')
                assert data['Sigma'].shape == (self.criteria_no, self.criteria_no)

        if self.alt_sort_number > 0 and isinstance(self.alternatives, type(None)):
            raise Exception("Alternatives should be given as input for the sorting problem!")

        return data

    def sampling(self):
        if self._check_input_data:
            posterior = stan.build(self.model, data=self.input_data, random_seed=1)
            self.samples = posterior.sample(num_chains=self.num_chains, num_samples=self.num_samples, num_warmup=100)
            self.process_samples() 
        else:
            raise Exception("The input data is not valid")

    def process_samples(self):
        self.dm_weight_samples = self.samples['W']
        self.dm_weight = np.mean(self.dm_weight_samples, axis=2)

        if self._is_clustering_required:
            self.cluster_center_samples = self.samples['wc']
            self.cluster_centers = np.mean(self.cluster_center_samples, axis=2)
            self.dm_membership_samples = self.samples['theta']
            self.dm_membership = np.mean(self.dm_membership_samples, axis=2)
            
        elif self._is_sorting_required:
            self.aggregated_weight_samples = self.samples['wStar']
            self.aggregated_weight = np.mean(self.aggregated_weight_samples, axis=1)
            
            soft_z_un = np.mean(self.samples['soft_z'], axis=2)
            soft_z = np.exp(soft_z_un)
            sum_soft_z = np.sum(soft_z, axis=1).reshape((self.alt_no, 1))
            self.alternative_membership = np.divide(soft_z, sum_soft_z)
            self.alternative_sorting = np.argmax(soft_z, axis=1)

            self.alternative_values = 1 / (1 + np.exp(-self.samples['v']))

            mu_un = np.mean(self.samples['altMu'], axis=1)
            self.sorting_centers = 1 / (1 + np.exp(-mu_un))
        
        else:
            self.aggregated_weight_samples = self.samples['wStar']
            self.aggregated_weight = np.mean(self.aggregated_weight_samples, axis=1)
    
    def exec_async(func, *args, **kwargs):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

class MCDMProblemOld(ABC):
    _basic_model = ""
    _basic_model_clustering = ""
    _basic_model_sorting = ""

    _correlated_model = ""
    _correlated_model_clustering = ""
    _correlated_model_sorting = ""

    _is_correlated_model = False
    _is_clustering_required = False
    _is_sorting_required = False

    def __init__(self, alternatives, dm_cluster_number, alt_sort_number, num_chain, num_samples, opt={}):
        self.alternatives = alternatives
        self.dm_cluster_no = dm_cluster_number
        self.alt_sort_no = alt_sort_number
        self.num_chains = num_chain
        self.num_samples = num_samples
        self.options = opt

        #self._isCorrelatedModel = False if (isinstance(self.Alternatives, type(None)) and self.Options.get('CriteriaIndependence') == (False or None)) else True
        if self.alternatives is not None or self.options.get('Sigma') is not None:
            self._is_correlated_model = True
        if self.options.get('CriteriaDependence') == False:
            self._is_correlated_model = False

        self._is_sorting_required =  True if self.alt_sort_no > 0 else False
        self._is_clustering_required = True if self.dm_cluster_no > 0 else False


    @property
    def alt_no(self):
        return 0 if isinstance(self.alternatives, type(None)) else self.alternatives.shape[0]

    @abstractproperty
    def input_data(self):
        pass

    @abstractproperty
    def dm_no(self):
        pass
    
    @abstractproperty
    def criteria_no(self):
        pass
    
    @abstractmethod
    def _check_input_data(self):
        pass

    @property
    def Model(self):
        model = 'self._'

        model = model + 'correlated_model' if self._is_correlated_model  else model + 'basic_model'
        model = model + 'Clustering' if self._is_clustering_required else model
        model = model + 'Sorting' if self._is_sorting_required else model 

        print("The used model is: ", model)
        return eval(model)

    def _getCommonData(self):
        data = {}
        data['DmNo'] = self.dm_no
        data['CNo'] = self.criteria_no

        if self.dm_cluster_no > 0:
            data['DmC'] = self.dm_cluster_no

        if not isinstance(self.alternatives, type(None)):
            data['Alt'] = self.alternatives
            data['AltNo'] = self.alt_no

        if self.alt_sort_no > 0:
            data['AltC'] = self.alt_sort_no
            data['eAlt'] = np.ones(self.alt_sort_no)

        if self._is_correlated_model:
            data['mu'] = 0.01 * np.ones(self.criteria_no)
            data['Sigma'] = np.cov(self.alternatives.T) #np.eye(self.CNo) #
            if not isinstance(self.options.get('Sigma'), type(None)):
                data['Sigma'] = self.options.get('Sigma')
                assert data['Sigma'].shape == (self.criteria_no, self.criteria_no)


        if self.alt_sort_no > 0 and isinstance(self.alternatives, type(None)):
            raise Exception("Alternatives should be given as input for the sorting problem!")

        return data

    def sampling(self):
        if self._checkInputData:
            posterior = stan.build(self.Model, data=self.inputData, random_seed=1)
            self.Samples = posterior.sample(num_chains=self.numChains, num_samples=self.numSamples)

            #posterior = self.exec_async(stan.build, self.Model, data=self.inputData, random_seed=1)
            #self.Samples = self.exec_async(posterior.sample, num_chains=self.numChains, num_samples=self.numSamples)
            self.processSamples() 
        else:
            raise Exception("The input data is not valid")

    def processSamples(self):
        self.DmWeightSamples = self.Samples['W']
        self.DmWeight = np.mean(self.DmWeightSamples, axis=2)

        if self._is_clustering_required:
            self.ClusterCenterSamples = self.Samples['wc']
            self.ClusterCenters = np.mean(self.ClusterCenterSamples, axis=2)
            self.DmMembershipSamples = self.Samples['theta']
            self.DmMembership = np.mean(self.DmMembershipSamples, axis=2)

        elif self._is_sorting_required:
            self.AggregatedWeightSamples = self.Samples['wStar']
            self.AggregatedWeight = np.mean(self.AggregatedWeightSamples, axis=1)
            
            soft_z_un = np.mean(self.Samples['soft_z'], axis=2)
            soft_z = np.exp(soft_z_un)
            sum_soft_z = np.sum(soft_z, axis=1).reshape((self.alt_no,1))
            self.AlternativeMembership = np.divide(soft_z, sum_soft_z)
            self.AlternativeSorting = np.argmax(soft_z, axis=1)

            self.AlternativeValues = 1 / (1 + np.exp(-self.Samples['v']))

            mu_un = np.mean(self.Samples['altMu'], axis=1)
            self.SortingCenters = 1 / (1 + np.exp(-mu_un))
        
        else:
            self.AggregatedWeightSamples = self.Samples['wStar']
            self.AggregatedWeight = np.mean(self.AggregatedWeightSamples, axis=1)
    
    def exec_async(func, *args, **kwargs):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

        

     
