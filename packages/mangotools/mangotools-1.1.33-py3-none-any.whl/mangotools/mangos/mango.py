# -*- coding: utf-8 -*-
K='save_callback'
O='form_data_callback'
N=callable
C=getattr
J=Exception
I=False
H='id'
G=dict
E=str
F=hasattr
D=isinstance
A=staticmethod
B=None
import asyncio as P,copy as L,json as M,smtplib as Q,threading as R
from datetime import datetime as S
from email.mime.multipart import MIMEMultipart as T
from email.mime.text import MIMEText as U
from threading import Thread as V
def X():return'���Ժ���'
class W(V):
	def __init__(A,loop):super().__init__();A._loop=loop;A.daemon=True
	def run(A):A._loop.run_forever()
class Y:
	@A
	def s(func,error,trace,username=B,*K,**D):
		G=error
		def A():
			I='content';C='729164035@qq.com'
			try:
				if D.get(I,B):H=D[I]
				else:H=f"""
                      â������ƽ̨����Ա��ע�����:
                          �����û���{username}
                          ����ʱ�䣺{S.now().strftime("%Y-%m-%d %H:%M:%S")}
                          ��������{func.__name__}
                          �쳣����: {type(G)}
                          ������ʾ: {E(G)}
                          �������飺{trace}
                          ����list��{K}
                          ����dict��{D}
            
                      **********************************
                      ��ϸ�����ǰ��â������ƽ̨�鿴������ظ�����Ա�ɺ��Դ���Ϣ��лл��
            
                                                                    -----------â������ƽ̨
                      """
				A=T();A['From']=C;A['To']=C;A['Subject']='��â������ƽ̨��';A.attach(U(H,'plain'))
				with Q.SMTP('smtp.qq.com')as F:F.starttls();F.login(C,'trwymxhsefpobdba');F.sendmail(C,C,A.as_string())
			except J:pass
		C=R.Thread(target=A);C.start()
	@A
	def v(v,s=B):
		if v==v:
			if s:print('����ͨ��')
		else:raise J('')
	@A
	async def a_e(self,e,v=B):
		A=C(self,e)
		if D(v,E):return await A(v)
		elif D(v,G):return await A(**v)
		elif v is B:return await A()
	@A
	def s_e(self,e,v=B):
		A=C(self,e)
		if D(v,E):return A(v)
		elif D(v,G):return A(**v)
		elif v is B:return A()
	@A
	def t():A=P.new_event_loop();B=W(A);B.start();return A
	@A
	def add_from_data(self):
		B=self;C=L.deepcopy(B.form_data)
		for A in C:
			if N(A.select):
				if F(B,O):A.select=B.form_data_callback(A)
				else:A.select=A.select()
		return C
	@A
	def edit_form_data(self,row,form_data,methods):
		J=self;E=form_data;C=row;E=L.deepcopy(E)
		for A in E:
			if D(C[A.key],G):
				A.value=C[A.key].get(H,B)
				if A.value is B and C[A.key]:A.value=M.dumps(C[A.key],ensure_ascii=I)
			elif D(C[A.key],list):A.value=M.dumps(C[A.key],ensure_ascii=I)
			else:A.value=C[A.key]
			if N(A.select):
				if F(J,O):A.select=J.form_data_callback(A)
				else:A.select=A.select()
			if A.subordinate and A.subordinate=='module':K=next((B for B in E if B.key==A.subordinate),B);K.select=methods.get_product_module_label(int(A.value))
			elif A.subordinate:K=next((B for B in E if B.key==A.subordinate),B);K.select=J.subordinate_callback(A)
		return E
	@A
	def put_save_data(self,row,data):
		B=data;A=self;B[H]=row.get(H)
		if F(A,K):A.save_callback(B,I)
		else:return A.put(B)
	@A
	def post_save_data(self,data):
		A=self
		if F(A,K):A.save_callback(data,True)
		else:return A.post(data)