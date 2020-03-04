
##### INÍCIO DO PROGRAMA ######################################################

from math import sqrt, ceil

##### DESCRIÇÃO DAS VARIÁVEIS #################################################

# b_w:      Largura da viga (ou largura da alma da viga, para 'seção T')
# d:        Altura útil da seção transversal da viga
# dominio   Domínio de deformação (NBR 6118/2014)
# E_c:      Módulo de Elasticidade do concreto (Módulo de Young)
# E_s:      Módulo de Elasticidade do aço CA-50 (Módulo de Young)
# epsilon_c Deformação no concreto
# epsilon_s Deformação no aço
# f_ck:     Resistência à compressão (característica) do concreto
# f_cd:     Resistência à compressão (de cálculo) do concreto
# gama_d    Coeficiente de majoração dos esforços
# gama_c    Coeficiente de minoração de resistência do concreto
# gama_s    Coeficiente de minoração de resistêcia do aço CA-50
# h:        Altura da seção da seção transversal viga
# M_Sk:     Momento Fletor Solicitante caracterísico do concreto
# M_Sd:     Momento Fletor Solicitante de cálculo do concreto
# sigma_s   Tensão de tração atuante no aço
# V_Sk:     Esforço Cortante SOlicitante característico do concreto
# V_Sd:     Esforço Cortante SOlicitante de cálculo do concreto
# z:        Braço de alavanca

# -----------------------------------------------------------------------------

##### DADOS FORNECIDOS PELO USUÁRIO ###########################################

f_ck = 30 
M_Sk = 6
b_w  = 15
h    = 40
d    = h-3

print('\nDIMENSIONAMENTO DE VIGAS DE CONCRETO ARMADO\n')

f_ck = float(input('Resistência do concreto:       f_ck [MPa] = '))
M_Sk = float(input('Momento Fletor Característico: M_Sk [tfm] = '))
b_w  = float(input('Largura da seção da viga:      b_w [cm]   = '))
h    = float(input('Altura da seção da viga:       h [cm]     = '))
d    = float(input('Altura útil da viga:           d [cm]     = '))

f_yk = 500
E_c  = 5600 * sqrt(f_ck)
E_s  = 210000

dados_entrada = (E_c , E_s , f_ck)

# -----------------------------------------------------------------------------

##### CONVERSÃO DE UNIDADES ###################################################

# Os cálculos são realizados com as unidades convertidas para o Sistema 
# Internacional (SI), sendo:

#  - Esforço Cortante (e forças em geral) em 'Newton' (N)
#  - Momento Fletor em 'Newton-metro' (N.m)
#  - Tensão Axial e Módulo de Elasticidade (Módulo de Young) em 'Pascal' (Pa)
#  - Medidas de espaço (dimensões da viga: base, altura) em 'metro' (m)

# -------------------------------------

### Sistema de Unidades adotado pelo usuário:

sist_unidades = 1

# sist_unidades = 0
#  - Momento Fletor em quilonewton-metro (kN.m)
#  - Esforço Cortante em quilonewton (kN)

# sist_unidades = 1
#  - Momento Fletor em tonelada-força-metro (tf.m)
#  - Esforço Cortante em tonelada-força (tf)

# -------------------------------------

### Matriz de Conversão (do sistema adotado pelo usuário para o SI)

# [0] Tensão      --> 1 MPa  = 1 000 000 Pa = 1 000 000 N/m²
# [1] Momento     --> 1 tf.m = 1000 kgf.m   = 10 000 N.m
# [2] Força       --> 1 tf   = 1000 kgf     = 10 000 N
# [3] Base/Altura --> 1 cm   = 0.01 m 

# Obs.: Adotando aceleração gravitacional g = 10 m/s²

if  sist_unidades  == 0:
    conversor = [1000000 , 1.000 , 1.000 , 0.01]

elif sist_unidades == 1:
    conversor = [1000000 , 10000 , 10000 , 0.01]   

# -------------------------------------

### Conversão dos dados de entrada para o Sistema Internacional

E_s  = conversor[0] * E_s
f_ck = conversor[0] * f_ck
f_yk = conversor[0] * f_yk
M_Sk = conversor[1] * M_Sk
b_w  = conversor[3] * b_w
h    = conversor[3] * h
d    = conversor[3] * d

# -----------------------------------------------------------------------------

##### TABELAS NBR #############################################################

### Área Nominal das barras de aço CA=50 (em cm²)

area_aco = {
    6.3  : 0.312 ,
    8    : 0.503 ,
    10   : 0.785 ,
    12.5 : 1.227 ,
    16   : 2.011 ,
    20   : 3.142 ,
    25   : 4.909 ,
    32   : 8.042 ,
    }

# -------------------------------------

### Taxa Mínima de Armadura (NBR-6118/2014)

taxa_arm_min = {
    20 : 0.150 , 25 : 0.150 , 30 : 0.150 ,
    35 : 0.164 , 40 : 0.179 , 45 : 0.194 ,
    50 : 0.208 , 55 : 0.211 , 60 : 0.219 ,
    65 : 0.226 , 70 : 0.233 , 75 : 0.239 ,
    80 : 0.245 , 85 : 0.251 , 90 : 0.256 ,   
    }

# -----------------------------------------------------------------------------

##### DEFINIÇÃO DAS FUNÇÕES ###################################################

### Cálculo da posição da Linha Neutra

def linha_neutra (f_cd , M_Sd , b_w , d):
    """
    Calcula a posição da Linha Neutra, medida a partir do banzo mais comprimido
   
    """
    k = M_Sd / (b_w * f_cd)
    x = (0.68 * d - sqrt (0.4624 * d**2 - 1.088 * k)) / 0.544
    return x

# -------------------------------------

### Cálculo das deformações e Domínios de Deformação (NBR-6118/2014)

def deformacoes (d , x):
    """
    1 - Calcula as deformações no concreto (compressão) e no aço (tração)
    2 - Determina o Domínio de Deformação segundo a NBR-6118/2014
   
    """
    # Limites de Deformação estabelecidos pela NBR-6118/2014
    epsilon_c_lim = 0.0035      # Deformação limite do concreto
    epsilon_s_esc = 0.00207     # Deformação de escoamento do aço CA-50
    epsilon_s_lim = 0.010       # Deformação limite do aço CA-50

    # Cálculo das deformações pela Equação de Compatibilidade
    epsilon_c = epsilon_s_lim * (x / (d - x))       # Deformação no concreto
    epsilon_c = min (epsilon_c , epsilon_c_lim)
    epsilon_s = epsilon_c_lim * ((d - x) / x)       # Deformação no aço
    epsilon_s = min (epsilon_s , epsilon_s_lim)

    # Determinação do Domínio de Deformação (NBR-6118/2014)
    if epsilon_c == epsilon_c_lim:
        if epsilon_s < epsilon_s_esc:    # ε_c = 3,5 ‰  ∧  ε_s < 2,07 ‰
            dominio = '4' 
        elif epsilon_s == epsilon_s_esc: # ε_c = 3,5 ‰  ∧  ε_s = 2,07 ‰
            dominio = '3-4'
        elif epsilon_s == epsilon_s_lim: # ε_c = 3,5 ‰  ∧  < ε_s = 10 ‰
            dominio = '2-3'
        else:                            # ε_c = 3,5 ‰  ∧  2,07 ‰ < ε_s <= 10 ‰
            dominio = '3' 
    else:                                # ε_c < 3,5 ‰  ∧  ε_s = 10 ‰
        dominio = '2'

    return epsilon_c , epsilon_s, dominio

# -------------------------------------

### Cálculo da Armadura Longitudinal

def tensao_aco (dominio , epsilon_s , E_s , f_yd):
    """
    Calcula a Tensão de tração no aço.

    Nos domíníos 2, 2-3, 3 e 3-4 o aço se encontra no patamar de escoamento, 
    portanto, a tensão no mesmo é igual a tensão de escoamento (σ_s = f_yd).

    No domínio 4 o aço se encontra no regime elástico, sendo calculado em 
    função de sua deformação longitudinal e seu Módulo de Elasticidade.

    """
    if dominio == 4:
        sigma_s = E_s * epsilon_s
    else:
        sigma_s = f_yd
    return sigma_s

# -------------------------------------

def armadura_longitudinal (M_Sd , z , sigma_s):
    """
    Calcula Armadura Longitudinal para resistir ao Momento Fletor solicitante

    """
    A_s = M_Sd / (z * sigma_s)
    return A_s

# -------------------------------------

def armadura_minima_long (b_w , h , f_ck_MPa):
    """
    Calcula a armadura mínima para a seção fornecida

    """
    if dados_entrada[2] % 5 == 0:
        pass
    else:
        f_ck_MPa = math.trunc(f_ck_MPa / 5) * 5

    if f_ck_MPa <= 30:
        rho_minimo = 0.15
    else:
        rho_minimo = taxa_arm_min[f_ck_MPa]

    A_smin = (rho_minimo * 0.01) * b_w * h

    return A_smin

# -------------------------------------

##### OBTENÇÃO DOS ESFORÇOS SOLICITANTES E RESISTÊNCIAS DE CÁLCULO ############

### Coeficientes de majoração e minoração

gama_d = 1.40 
gama_c = 1.40
gama_s = 1.10

### Esforços de Cálculo

M_Sd = M_Sk * gama_d
# V_Sd = V_Sk * gama_d

### Resistências de Cálculo

f_cd = f_ck / gama_c
f_yd = f_yk / gama_s

# -----------------------------------------------------------------------------

##### DIMENSIONAMENTO À FLEXÃO - ESTADO LIMITE ÚLTIMO (ELU) ###################

### Cálculo da Linha Neutra

x = linha_neutra (f_cd, M_Sd, b_w, d)

### Deformações no concreto e no aço

epsilon_c = deformacoes (d, x) [0]
epsilon_s = deformacoes (d, x) [1]
dominio   = deformacoes (d, x) [2]

### Cálculo da Armadura Longitudinal

z = d - 0.4 * x

sigma_s = tensao_aco (dominio , epsilon_s , E_s , f_yd)

A_s = armadura_longitudinal (M_Sd , z , sigma_s)

### Cálculo da Armadura Longitudinal Mínima (NBR-6118/2014)

f_ck_MPa = dados_entrada[2]
A_smin   = armadura_minima_long (b_w , h , f_ck_MPa)

# -----------------------------------------------------------------------------

##### IMPRESSÃO DOS RESULTADOS ###################

item_1 = 'Posição da Linha Neutra:'
item_2 = 'Domínio:'
item_3 = 'Armadura Longitudinal:'
item_4 = 'Armadura Mínima:' 

print()

print('{} {} {}'
.format(item_1 , str(round(x * 100 , 2)).rjust(5),'cm'.rjust(0)))

print('{} {} {}'
.format(item_2 , dominio.rjust(17) ,''))

print('{} {} {}'
.format(item_3 , str(round(A_s * 10000 , 2)).rjust(6) ,'cm²'.rjust(4)))

print('{} {} {}'
.format(item_4 , str(round(A_smin * 10000 , 2)).rjust(11) ,'cm²'.rjust(5)))

n_10_0 = A_s * 10000 / area_aco[10]
n_12_5 = A_s * 10000 / area_aco[12.5]

print()
print('Armação: {} φ 10 ou {} φ 12.5 \n'.format(ceil(n_10_0) , ceil(n_12_5)))


##### FIM DO PROGRAMA #########################################################
