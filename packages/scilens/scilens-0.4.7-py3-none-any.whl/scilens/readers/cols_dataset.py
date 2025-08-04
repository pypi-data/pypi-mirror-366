_E='charts'
_D='x_index'
_C='csv_col_index'
_B='curves'
_A=None
import logging
from dataclasses import dataclass,field
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
from scilens.config.models.reader_format_cols import ReaderCurveParserNameConfig
from scilens.config.models.reader_metrics import ReaderColsMetricsConfig
def get_index_col_index(index_col,numeric_col_indexes,names):
	C=names;A=index_col;B=_A
	if isinstance(A,int):B=A-1
	if isinstance(A,str):A=[A]
	if isinstance(A,list):
		for D in A:
			if D in C:B=C.index(D);break
	if B:
		if B not in numeric_col_indexes:raise ValueError(f"Index column index {A} is not a numeric column.")
	return B
@dataclass
class ColsDataset:
	cols_count:int=0;rows_count:int=0;names:list[str]=field(default_factory=lambda:[]);numeric_col_indexes:list[int]=field(default_factory=lambda:[]);data:list[list[float]]=field(default_factory=lambda:[]);origin_line_nb:list[int]=field(default_factory=lambda:[])
	def get_curves_col_x(I,col_x):
		H='title';D=col_x;A=I;F={};C=get_index_col_index(D,A.numeric_col_indexes,A.names);F[_D]=C;J=[B for(A,B)in enumerate(A.numeric_col_indexes)if A!=C];E=[];G=[]
		for B in J:D=A.data[C];K=A.data[B];L={H:A.names[B],'short_title':A.names[B],'series':[[D[A],K[A]]for A in range(A.rows_count)],_C:B};E+=[L];M={H:A.names[B],'type':'simple','xaxis':A.names[C],'yaxis':A.names[B],_B:[len(E)-1]};G+=[M]
		return{_B:E,_E:G},F
	def compute_metrics(I,config):
		D=I;H={}
		for A in config:
			E=A.col;B=_A
			if isinstance(E,int):B=D.numeric_col_indexes.index(E-1)
			if isinstance(E,str):B=D.names.index(E)
			if B is _A or B<0 or B>=D.cols_count:raise ValueError(f"Metric '{A.name}' has an invalid column: {E}. Skipping.")
			G=A.name
			if not G:G=f"{D.names[B]} {A.aggregation}"
			F=D.data[B];C=_A
			if A.aggregation=='mean':C=sum(F)/len(F)
			elif A.aggregation=='sum':C=sum(F)
			elif A.aggregation=='min':C=min(F)
			elif A.aggregation=='max':C=max(F)
			if C is _A:raise ValueError(f"Metric '{A.name}' has an invalid aggregation: {A.aggregation}.")
			H[G]=C
		return H
@dataclass
class ColsCurves:type:str;info:dict;curves:dict
def compare(group,compare_floats,reader_test,reader_ref,cols_curve):
	O='Errors limit reached';F=reader_ref;D=group;C=cols_curve;A=reader_test;logging.debug(f"compare cols: {D.name}")
	if len(A.numeric_col_indexes)!=len(F.numeric_col_indexes):D.error=f"Number Float columns indexes are different: {len(A.numeric_col_indexes)} != {len(F.numeric_col_indexes)}";return
	E=[''for A in range(A.cols_count)];I=_A;G=_A
	if C and C.type==ReaderCurveParserNameConfig.COL_X:J=C.info[_D];I=A.data[J];G=A.names[J]
	K=False
	for B in range(A.cols_count):
		if B not in A.numeric_col_indexes:continue
		P=A.data[B];Q=F.data[B];logging.debug(f"compare cols: {A.names[B]}");L,R,T=compare_floats.add_group_and_compare_vectors(A.names[B],D,{'info_prefix':G}if G else _A,P,Q,info_vector=I)
		if R:K=True;E[B]=O;continue
		if L.total_errors>0:E[B]=f"{L.total_errors} comparison errors"
	if C:
		for M in C.curves[_E]:
			N=0
			for S in M[_B]:
				H=C.curves[_B][S]
				if E[H[_C]]:H['comparison_error']=E[H[_C]];N+=1
			M['comparison']={'curves_nb_with_error':N}
	D.error=O if K else _A;D.info={'cols_has_error':E}