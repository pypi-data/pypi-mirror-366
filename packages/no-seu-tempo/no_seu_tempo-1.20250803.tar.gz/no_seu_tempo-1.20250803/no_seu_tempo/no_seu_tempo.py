import re
from datetime import date, timedelta
from dateutil.easter import easter
from calendar import monthrange
from dateutil.relativedelta import relativedelta


MES_GENERICO = 30
NOMES_MESES = (
    'janeiro','fevereiro',  'março',
    'abril',  'maio',       'junho',
    'julho',  'agosto',  'setembro',
    'outubro','novembro','dezembro'
)
DIAS_SEMANA = {
    'segunda': 0,
    'terça': 1, 'terca': 1,
    'quarta': 2,
    'quinta': 3,
    'sexta': 4,
    'sábado': 5, 'sabado': 5,
    'domingo': 6,
}
PREFIXO_ULT = '[úu]ltimo dia d[eo]'
SUFIXO_MES  = 'mês|mes'


class Feriado:
    @classmethod
    def no_ano(cls, ano: int) -> date:
        raise NotImplementedError('Use as classes filhas de Feriado')
    
    @classmethod
    def nome(cls):
        return cls.__name__.lower()

class Carnaval(Feriado):
    @classmethod
    def no_ano(cls, ano: int) -> date:
        return easter(ano) - timedelta(days=47)

class Natal(Feriado):
    @classmethod
    def no_ano(cls, ano: int) -> date:
        return date(ano, 12, 25)


class NoSeuTempo:
    """
    Escreva a data como você fala! ;)
    ---
    """
    DT_ATUAL = None
    UNIDADES_TEMPO = {
        'dias': 1, 'semana': 7, 'semanas': 7,
        'mês': MES_GENERICO,'mes': MES_GENERICO, 'meses': MES_GENERICO,
        'ano': 365, 'anos': 365
    }

    @staticmethod
    def numero_do_mes(mes: str) -> int:
        for i, nome in enumerate(NOMES_MESES, 1):
            if nome == mes or mes == nome[:3]:
                return i
        return -1
  
    def dia_da_semana(self, txt: str) -> int:        
        dia, *_ = re.split(r'[-]feira', txt)
        if dia not in DIAS_SEMANA:
            return -1
        return DIAS_SEMANA[dia]

    def data_fixa(self, txt: str) -> date:
        separadores = r'(\s+de\s+|[-/])'
        por_extenso = re.findall(fr'(\d+){separadores}(\w+|\d+){separadores}*(\d+)*', txt)
        if por_extenso:
            dia, _, mes, _, ano =  por_extenso[0]
            if not ano:
                ano = self.DT_ATUAL.year
            if mes.isalpha():
                mes = self.numero_do_mes(mes)
                if mes == -1:
                    return None
            return date( int(ano), int(mes), int(dia) )
        return None
    
    def data_por_nome(self, txt: str) -> date:
        EXPRESSOES_DE_DATA =  {
            "hoje":   0, "ontem":  -1, "amanhã": +1, "anteontem": -2,
        }
        if txt in EXPRESSOES_DE_DATA:
            num = EXPRESSOES_DE_DATA[txt]
            return self.DT_ATUAL + timedelta(days=num)
        return None
    
    def converte_unidade_tempo(self, unidade: str, num: int=1):
        dias = self.UNIDADES_TEMPO[unidade]
        if dias == MES_GENERICO:
            return relativedelta(months=num)
        return timedelta(days=dias * num)
    
    def data_relativa(self, txt: str) -> date:
        BUSCAS = (r'em (\d+) (\w+)', r'daqui a (\d+) (\w+)', r'(\d+) (\w+) atrás')
        POS_NEGATIVA = 2
        for i, regex in enumerate(BUSCAS):
            encontrado = re.findall(regex, txt)
            if encontrado:
                num, unidade = encontrado[0]
                if i == POS_NEGATIVA: 
                    num = f'-{num}' # número negativo
                break
        if not encontrado or unidade not in self.UNIDADES_TEMPO:
            return None
        return self.DT_ATUAL + self.converte_unidade_tempo(unidade, int(num))
    
    @staticmethod
    def expr_referencial(conteudo: str=r'\w+', substituir_ultimo: bool=False) -> list:
        lista_expr = [
            fr'pr[óo]xim[ao]\s+({conteudo})', fr'({conteudo})\s+que vem',
            fr'({conteudo})\s+passad[ao]', fr'[úu]ltim[oa]\s+({conteudo})',
        ]
        if substituir_ultimo:
            lista_expr[-1] = fr'{conteudo}\s+anterior'
        return lista_expr
    
    def data_aproximada(self, txt: str) -> date:
        POS_NEGATIVA = [2, 3]
        for i, regex in enumerate(self.expr_referencial()):
            encontrado = re.findall(regex, txt)
            if not encontrado:
                continue
            unidade = encontrado[0]
            num = -1 if i in POS_NEGATIVA else 1
            if unidade not in self.UNIDADES_TEMPO:
                dia_procurado = self.dia_da_semana(unidade)
                if dia_procurado == -1:
                    return None
                resultado = self.DT_ATUAL + timedelta(days=num)
                while resultado.weekday() != dia_procurado:
                    resultado += timedelta(days=num)
                return resultado
            break
        if not encontrado:
            return None
        return self.DT_ATUAL + self.converte_unidade_tempo(unidade, num)
    
    def data_apenas_dia(self, txt: str) -> date:
        encontrado = re.findall(r'dia\s+(\d+)(.*)', txt)
        if not encontrado:
            return None
        dia, *resto = encontrado[0]
        dia = int(dia)
        if not resto:
            return self.DT_ATUAL.replace(day=dia)
        mes = self.extrai_mes(resto[0])
        return date(self.DT_ATUAL.year, mes, dia)
    
    def carnaval(self, ano: int) -> date:
        return easter(ano) - timedelta(days=47)
    
    def natal(self, ano: int) -> date:
        return date(ano, 12, 25)
    
    def data_feriado(self, txt: str) -> date:
        POS_NEGATIVA = [2, 3]
        CLASSES_FERIADO = {
            cls.nome(): cls for cls in Feriado.__subclasses__()
        }
        BUSCAS = self.expr_referencial( '|'.join(CLASSES_FERIADO) )
        resultado = None
        for i, regex in enumerate(BUSCAS):
            encontrado = re.findall(regex, txt)
            if not encontrado or encontrado[0] not in CLASSES_FERIADO:
                continue
            cls = CLASSES_FERIADO[encontrado[0]]
            resultado = cls.no_ano(self.DT_ATUAL.year)
            if i in POS_NEGATIVA and self.DT_ATUAL < resultado:
                resultado = cls.no_ano(self.DT_ATUAL.year - 1)
            elif self.DT_ATUAL > resultado:
                resultado = cls.no_ano(self.DT_ATUAL.year + 1)
        return resultado

    def extrai_mes(self, nome: str) -> int:
        if not nome or re.search(fr'^({SUFIXO_MES})$', nome):
            return self.DT_ATUAL.month
        mes = self.numero_do_mes(nome)
        if mes != -1:
            return mes
        BUSCAS = self.expr_referencial(SUFIXO_MES, True)
        POS_NEGATIVA = [2, 3]
        for i, regex in enumerate(BUSCAS):
            if not re.search(regex, nome):
                continue
            if i in POS_NEGATIVA:
                return self.DT_ATUAL.month - 1
            return self.DT_ATUAL.month + 1
        return -1

    def data_ultimo_dia(self, txt: str) -> date:
        encontrado = re.findall(fr'({PREFIXO_ULT})\s+(.*)', txt)
        if not encontrado:
            return None
        mes = self.extrai_mes(encontrado[0][-1])
        if mes == -1:
            return None
        dia = monthrange(self.DT_ATUAL.year, mes)[-1]
        return date(self.DT_ATUAL.year, mes, dia)

    def loc_semana(self, mes: int|str, dia_semana: int|str, incr: int=1, qtd: int=1) -> date:
        """Localiza o dia da semana dentro do mês"""
        ano = self.DT_ATUAL.year
        if isinstance(mes, str):
            mes = self.extrai_mes(mes)
            if mes == -1: return None
        if isinstance(dia_semana, str):
            dia_semana = self.dia_da_semana(dia_semana)
            if dia_semana == -1: return None
        ULTIMO_DIA = monthrange(ano, mes)[-1]
        if incr < 0:            
            pos = ULTIMO_DIA
        else:
            pos = 1
        dt_ref = None
        while pos > 0 or pos <= ULTIMO_DIA:
            dt_ref = date(ano, mes, pos)
            if dt_ref.weekday() == dia_semana:
                qtd -= 1
                if qtd == 0: break
            pos += incr
        return dt_ref
    
    @staticmethod
    def substitui_ordinal(txt: str) -> str:
        ORDINAIS = ['primeir', 'segund', 'terceir', 'quart',]
        RX_ORDINAIS = '|'.join(f'{expr}[ao]' for expr in ORDINAIS)
        encontrado = re.search(fr'^({RX_ORDINAIS})', txt)
        if encontrado:
            ini, fim = encontrado.span()
            pos = ORDINAIS.index(txt[ini:fim-1])+1
            txt = f'{pos}{txt[fim-1]}{txt[fim:]}'
        return txt
    
    def data_por_posicao_calend(self, txt: str) -> date:
        txt = self.substitui_ordinal(txt)
        pos, ord, neg, dia, sufx, prep, mes = (
            r'(\d+)',      r'([aªoº]\s+)', 
            r'([uú]ltim[ao]\s+)*',
            r'|'.join(DIAS_SEMANA),
            r'([-]feira\s+)*',
            r'(d[eo]\s+)*',      r'(.*)'
        )
        encontrado = re.findall(
            fr'{pos}{ord}{neg}({dia}){sufx}{prep}{mes}', txt
        )
        if not encontrado:
            return None
        pos, _, neg, dia, _, _, mes = encontrado[0]
        return self.loc_semana(mes, dia, -1 if neg else 1, int(pos))

    def __init__(self, txt: str):
        txt = txt.lower().strip()
        if not self.DT_ATUAL:
            self.DT_ATUAL = date.today()
        data = None
        self.metodo = ''
        METODOS = (
            self.data_fixa, self.data_por_nome,
            self.data_relativa, self.data_ultimo_dia,
            self.data_apenas_dia, self.data_por_posicao_calend,
            self.data_aproximada, self.data_feriado,            
        )
        for func in METODOS:
            data = func(txt)
            if data:
                self.metodo = func.__name__
                break
        self.data = data

    @classmethod
    def testar(cls):
        TESTES = [
            ('16/7/2023',                        '2023-07-16'),
            ('hoje',                             '2025-09-01'),
            ('ontem',                            '2025-08-31'),
            ('anteontem',                        '2025-08-30'),
            ('amanhã',                           '2025-09-02'),
            ('em 3 dias',                        '2025-09-04'),
            ('2 semanas atrás',                  '2025-08-18'),
            ('25 de novembro de 2024',           '2024-11-25'),
            ('25 de novembro',                   '2025-11-25'),
            ('dia  14',                          '2025-09-14'),
            ('25/nov',                           '2025-11-25'),
            ('próxima semana',                   '2025-09-08'),
            ('mês passado',                      '2025-08-01'),
            ('ano passado',                      '2024-09-01'),
            ('segunda passada',                  '2025-08-25'),
            ('última terça',                     '2025-08-26'),
            ('próxima quarta',                   '2025-09-03'),
            ('quinta que vem',                   '2025-09-04'),
            ('último natal',                     '2024-12-25'),
            ('próximo carnaval',                 '2026-02-17'),
            ('daqui a 15 dias',                  '2025-09-16'),
            ('último dia do mês        ',        '2025-09-30'),
            ('ultimo dia do mês passado',        '2025-08-31'),
            ('último dia do próximo mes',        '2025-10-31'),
            ('último dia do mês que vem',        '2025-10-31'),
            ('último dia de fevereiro  ',        '2025-02-28'),
            ('primeira segunda-feira de julho',  '2025-07-07'),
            ('3a ultima quinta               ',  '2025-09-11'),
            ('segundo domingo do próximo mês ',  '2025-10-12'),
            ('dia 14 do mes passado',            '2025-08-14'),
            #
            # P.S.: Evitar complicações,
            #       ... tipo "35 dias depois da 1a terça antes do carnaval de 2 anos atrás"
            #  > Ninguém fala assim!  :/ 
        ]
        cls.DT_ATUAL = date(2025, 9, 1)
        print('  ===============================================================================')
        titulo = '            Data de referência para teste: {} \n'.format(
            str(cls.DT_ATUAL)
        )
        print(titulo.center(50))
        print('  +-------------------------------------+------------+----------------------------+')
        print('  |                         Parâmetro   |  Resultado |      Método                |')
        print('  +-------------------------------------+------------+----------------------------+')
        for texto, esperado in TESTES:
            obj = cls(texto)
            resultado = obj.data
            assert str(resultado) == esperado
            print(f'  | {texto:>35} | {resultado} | {obj.metodo:<26} |')
        print('  +-------------------------------------+------------+----------------------------+')
        print('\n      (Resultado: 100% de sucesso!) \n')
        print('  ===============================================================================')


if __name__ == "__main__":
    NoSeuTempo.testar()
