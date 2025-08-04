# -*- coding: utf-8 -*-
M='m_0116'
R=isinstance
F='_id'
E='tools_error'
J='parent_id'
L=str
C='data'
I='log'
H=True
G='id'
D='response_data'
B='request'
import json as K,traceback as Q
def A(self,**A):
	Y='m_0001';X='field_does_note_xist';W='project_product_id__in';V='project_product';P='page';O='pageSize';K='case_sort';C=self;E={}
	for(J,M)in dict(A.get(B).query_params.lists()).items():
		if J and R(M[0],L)and J not in C.not_matching_str and G not in J:E[f"{J}__contains"]=M[0]
		else:E[J]=M[0]
	S=A.get(B).headers.get('Project',None)
	if S and hasattr(C.model,V):
		T=A.get(V).objects.filter(project_id=S)
		if C.model.__name__ in C.pytest_model:Z=A.get('pytest_product').objects.filter(project_product_id__in=T.values_list(G,flat=H));E[W]=Z.values_list(G,flat=H)
		else:E[W]=T.values_list(G,flat=H)
	try:
		if A.get(B).query_params.get(O)and A.get(B).query_params.get(P):
			del E[O],E[P]
			try:C.model._meta.get_field(K);F=C.model.objects.filter(**E).order_by(K)
			except A.get(X):F=C.model.objects.filter(**E)
			a,b=C.paging_list(A.get(B).query_params.get(O),A.get(B).query_params.get(P),F,C.get_serializer_class());return A.get(D).success(A.get(Y),a,b)
		else:
			try:C.model._meta.get_field(K);F=C.model.objects.filter(**E).order_by(K)
			except A.get(X):F=C.model.objects.filter(**E)
			U=C.get_serializer_class()
			try:F=U.setup_eager_loading(F)
			except A.get('field_error'):pass
			return A.get(D).success(A.get(Y),U(instance=F,many=H).data,F.count())
	except A.get('s3_error')as N:A.get(I).system.error(f"GET�������쳣�����Ų����⣺{N}, error:{Q.print_exc()}");return A.get(D).fail(A.get('m_0026'))
	except Exception as N:A.get(I).system.error(f"GET�������쳣�����Ų����⣺{N}, error:{Q.print_exc()}");return A.get(D).fail(A.get('m_0027'))
def N(self,**A):
	C=self.serializer(data=A.get(B).data)
	if C.is_valid():C.save();self.asynchronous_callback(A.get(B).data.get(J));return A.get(D).success(A.get('m_0002'),C.data)
	else:A.get(I).system.error(f"ִ�б���ʱ�������飡���ݣ�{A.get(B).data}, ������Ϣ��{K.dumps(C.errors)}");return A.get(D).fail(A.get('m_0003'),C.errors)
def O(self,**A):
	E=self
	if R(A.get(B),dict):F=A.get(B);C=E.serializer(instance=E.model.objects.get(pk=A.get(B).get(G)),data=F,partial=H)
	else:F=A.get(B).data;C=E.serializer(instance=E.model.objects.get(pk=A.get(B).data.get(G)),data=F,partial=H)
	if C.is_valid():C.save();E.asynchronous_callback(A.get(B).data.get(J));return A.get(D).success(A.get('m_0082'),C.data)
	else:A.get(I).system.error(f"ִ���޸�ʱ�������飡���ݣ�{F}, ������Ϣ��{L(C.errors)}");return A.get(D).fail(A.get('m_0004'),C.errors)
def P(self,**A):
	C=self;F=A.get(B).query_params.get(G);H=[int(A)for A in A.get(B).query_params.getlist('id[]')]
	try:
		if not F and H:
			for K in H:C.model.objects.get(pk=K).delete()
		else:C.model.objects.get(id=F).delete();C.asynchronous_callback(A.get(B).query_params.get(J))
	except A.get(E)as I:return A.get(D).fail((I.code,I.msg))
	except C.model.DoesNotExist:return A.get(D).fail(A.get('m_0029'))
	else:return A.get(D).success(A.get('m_0005'))
def S(cls,**A):
	B=cls.serializer(data=A.get(C))
	if B.is_valid():B.save();return B.data
	else:A.get(I).system.error(f"ִ���ڲ�����ʱ�������飡���ݣ�{A.get(C)}, ������Ϣ��{K.dumps(B.errors)}");raise A.get(E)(*A.get(M),value=(B.errors,))
def T(cls,**A):
	B=cls.serializer(instance=cls.model.objects.get(pk=A.get(F)),data=A.get(C),partial=H)
	if B.is_valid():B.save();return B.data
	else:A.get(I).system.error(f"ִ���ڲ��޸�ʱ�������飡id:{A.get(F)}, ���ݣ�{A.get(C)}, ������Ϣ��{L(B.errors)}");raise A.get(E)(*A.get(M),value=(B.errors,))
def U(cls,**A):cls.model.objects.get(id=A.get(F)).delete()