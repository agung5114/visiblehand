import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
import plotly.graph_objects as go
# from PIL import Image
st.set_page_config(layout='wide')
# import plotly.io as pio
# pio.templates
# pio.templates.default = "simple_white"
# load model 
# import joblib

# linear programming
import pulp
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable

def main():
    st.title("Simulasi Realokasi Budget untuk memaksimalkan Efisiensi dan Omset")
    menu = ["Simulasi_LP","Analisis"]
    choice = st.sidebar.selectbox("Select Menu", menu)

    if choice == "Simulasi_LP":
        df = pd.read_excel('UMKM_Efisiensi.xlsx')
        provinsi = st.sidebar.selectbox('Pilih Provinsi',df.Prov.unique())
        df = df[df['Prov'].isin([provinsi])]
        pemda = st.sidebar.selectbox('Pilih Pemda',df.Kab_APBD.unique())
        # pilihsektor = st.sidebar.selectbox('Pilih Potensi Sektoral',df.Potensi.unique().tolist())
        # df = df[df['Potensi'].isin([pilihsektor])]
        umkm = st.sidebar.selectbox('Pilih UMKM',['All']+df.BU.unique().tolist())
        # sektor= 'Cluster'
        # sektor = 'Sektor_group'
        # potensi = dfc.Potensi.tolist()
        # st.sidebar.write(f'Sektor_Potensial: {potensi[0]}')
        # sektor = dfc[sektor].tolist()
        # sektor = sektor[0]
        # # st.write(sektor)
        # st.sidebar.write(f'Tahun Anggaran  : {tahun}')
        # df = df[df['Pemda'].isin([pemda])]
        # anggaran = df[col].tolist()
        # # st.sidebar.write(f'Total Anggaran Berjalan : {anggaran[0]}')
        # st.sidebar.number_input(label="Total Realisasi Anggaran (Milyar Rupiah)",value=int(anggaran[0])/1000000000,min_value=0.0, max_value=1000000000.0, step=10.0)
        # nextangg = df[str("y"+str(tahun+1))].tolist()
        # # st.sidebar.write(f'Anggaran Tahun Berikutnya : {nextangg[0]}')
        # st.sidebar.number_input(label="Total Anggaran Tahun Berikutnya (Milyar Rupiah)",value=int(nextangg[0])/1000000000,min_value=0.0, max_value=1000000000.0, step=10.0)
        # efbase = int(dfc.Efisiensi.sum()*10000)/100
        # # st.sidebar.write(f'Potensi Sektoral  : {sektor}')
        st.title(umkm)
        if umkm=='All':
            st.write('Silakan Pilih UMKM')
        else:
            dfs = df[df['BU'].isin([umkm])]
            st.subheader(f'Nama Tempat Usaha: {dfs.Nama_pasar.values[0]}')
            st.subheader(f'Tingkat Efisiensi UMKM: {int(dfs.Efisiensi.mean()*10000)/100} %')
            st.subheader(f'Omset UMKM: {int(dfs.omset.sum())}')

            if int(dfs.Efisiensi.mean()*100) >84.9:
                st.subheader('UMKM eligible mendapatkan kredit')
            else:
                s1='Beban_UmumAdm'
                s2='Beban_Penjualan'
                s3='Beban_Lainnya'
                
                dfs = df[[s1,s2,s3,'Total_beban','BU']]
                dfs[s1] = dfs[s1]/dfs['Total_beban']
                dfs[s2] = dfs[s2]/dfs['Total_beban']
                dfs[s3] = dfs[s3]/dfs['Total_beban']
                dfm = pd.melt(dfs,id_vars=['BU'],value_vars=[s1,s2,s3])
                dflp = df[df['Kab_APBD'].isin([pemda])]
                dflp = dflp.replace(to_replace=0,value=np.NAN)
                top = dflp['Efisiensi'].max()
                # st.write(top)
                dflp = dflp[dflp['Efisiensi']>=top-0.05]
                with st.beta_expander('Daftar UMKM Frontier Wilayah', expanded=False):
                    st.write(dflp[['BU','Prov','Kab_APBD','Efisiensi','omset']])
                # dflp = dflp.replace(to_replace=0,value=np.NAN)
                kolom = dfm.variable.unique().tolist()
                f1=dflp[s1]/dflp['Total_beban']
                f2=dflp[s2]/dflp['Total_beban']
                f3=dflp[s3]/dflp['Total_beban']
                fig = go.Figure()
                fig.add_trace(go.Box(y=f1,name=s1))
                fig.add_trace(go.Box(y=f2,name=s2))
                fig.add_trace(go.Box(y=f3,name=s3))
                fig.add_trace(go.Scatter(x=kolom, y=dfm['value'],mode='lines',name=umkm))
                fig.update_layout(width=900,height=600,title="Perbandingan UMKM Terpilih Dengan Frontier Wilayah")
                st.plotly_chart(fig)

                with st.beta_expander('Efficiency Analysis', expanded=False):
                    c1,c2,c3,c4 = st.beta_columns((2,1,2,2))
                    with c1:
                        # bv = dfs.iloc[0,3:7].astype('float').tolist()
                        st.text_input(label=s1+" (%)",value=int(dfs[s1].mean()*10000)/100.0)
                        st.text_input(label=s2+" (%)",value=int(dfs[s2].mean()*10000)/100.0)
                        st.text_input(label=s3+" (%)",value=int(dfs[s3].mean()*10000)/100.0)
                    with c2:
                        st.empty()
                    with c3:
                        #min value
                        v1min = st.number_input(label=s1,value=f1.quantile(0.25)*100.0,min_value=0.0, max_value=100.0, step=1.0)
                        v2min = st.number_input(label=s2,value=f2.quantile(0.25)*100.0,min_value=0.0, max_value=100.0, step=1.0)
                        v3min = st.number_input(label=s3,value=f3.quantile(0.25)*100.0,min_value=0.0, max_value=100.0, step=1.0)
                    with c4:
                        #max value
                        v1max = st.number_input(label=s1,value=f1.max()*100.0,min_value=0.0, max_value=100.0, step=1.0)
                        v2max = st.number_input(label=s2,value=f2.max()*100,min_value=0.0, max_value=100.0, step=1.0)
                        v3max = st.number_input(label=s3,value=f3.max()*100.0,min_value=0.0, max_value=100.0, step=1.0)

                # Create the LP model
                prob = LpProblem(name="Allocation Optimization",sense=LpMaximize)
                # Initialize the decision variables
                v1 = LpVariable(name=s1, lowBound=0)
                v2 = LpVariable(name=s2, lowBound=0)
                v3 = LpVariable(name=s3, lowBound=0)
                bo = [-332304.0175,1.05645607860482,1.15648620346764,1.14590795340159]
                be = [0.846524,2.4740504346002E-11,-1.23825409764219E-12,2.85633816289292E-11]
                efscore= be[0]+v1*be[1]+v2*be[2]+v3*be[3]
                grscore = bo[0]+v1*bo[1]+v2*bo[2]+v3*bo[3]
                
                prob += grscore
                prob += efscore
                # prob += grscore
                # Add the constraints to the model
                prob += (v1+v2+v3 ==1, "full_constraint")
                prob += (v1*100 >= v1min, "v1min")
                prob += (v2*100 >= v2min, "v2min")
                prob += (v3*100 >= v3min, "v3min")
                prob += (v1*100 <= v1max, "v1max")
                prob += (v2*100 <= v2max, "v2max")
                prob += (v3*100 <= v3max, "v3max")
                prob += (efscore <=1, "maxEff")
                prob += (efscore >=0, "minEff")

                # Solve the problem
                st.write("Penghitungan Alokasi Beban Paling Efisien")
                if st.button("Klik untuk Jalankan"):
                    status = prob.solve()
                    p1 =  pulp.value(v1)
                    p2 =  pulp.value(v2)
                    p3 =  pulp.value(v3)
                    total = int((p1+p2+p3)*10000)/100
                    outls = [p1,p2,p3]
                    # st.subheader(outls)
                    h1,h2 = st.beta_columns((5,3))
                    
                    with h1:
                        fig1 = go.Figure()
                        fig1.add_trace(go.Bar(x=kolom, y=dfm['value'],name='Current Allocation'))
                        fig1.add_trace(go.Bar(x=kolom, y=outls,name='Recommendation'))
                        fig1.update_layout(width=700, height=600)
                        st.plotly_chart(fig1)
                    with h2:
                        # efficiency= ef[0]+ef[1]*bv[1]+ef[2]*bv[2]+ef[3]*bv[4]+ef[4]*bv[5]+p1*ef[5]+p2*ef[6]+p3*ef[7]+p4*ef[8]+p5*ef[9]+p6*ef[10]+p7*ef[11]+p8*ef[12]+p9*ef[13]
                        growth= bo[0]+p1*bo[1]+p2*bo[2]+p3*bo[3]
                        efficiency= be[0]+p1*be[1]+p2*be[2]+p3*be[3]
                        st.markdown('')
                        st.markdown('')
                        st.markdown('')
                        # st.write(status)
                        fig3 = go.Figure()
                        fig3.add_trace(go.Indicator(
                                        mode = "number+delta",
                                        # value = status*100,
                                        value = int(growth*100)/100,
                                        title = {"text": "Prediksi Tingkat Growth (%):"},
                                        delta = {'reference': int(df.omset.sum()*100)/100, 'relative': False},
                                        domain = {'x': [0, 0.5], 'y': [0.6, 1]},
                                        ))
                        fig3.add_trace(go.Indicator(
                                        mode = "number+delta",
                                        # value = status*100,
                                        value = int(efficiency*10000)/100,
                                        title = {"text": "Tingkat Efisiensi (%):"},
                                        delta = {'reference': int(df.Efisiensi.sum()*10000)/100, 'relative': False},
                                        domain = {'x': [0, 0.5], 'y': [0, 0.4]},
                                        ))
                        # fig3.update_layout(width=200)
                        st.plotly_chart(fig3)
                
if __name__=='__main__':
    main()