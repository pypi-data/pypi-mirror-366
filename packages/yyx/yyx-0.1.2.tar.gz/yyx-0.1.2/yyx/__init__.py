
from .corr import describe,jb_test,normalize,positivation,pearson
from .LinearRegression import ols,gls,hetero_test
from matplotlib import pyplot as plt

plt.rcParams['font.family'] = ['Times New Roman','Simhei']
plt.rcParams['axes.unicode_minus']= False
__all__=['describe','jb_test','normalize','positivation','pearson','gls','ols']