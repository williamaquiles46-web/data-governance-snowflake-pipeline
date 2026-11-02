Pipeline de Engenharia de Dados e Governança Transacional (Python e Snowflake)
Visão Geral do Projeto:

Este projeto implementa um pipeline de engenharia de dados baseado nos princípios de Shift-Left Data Quality e Governança Transacional. A solução integra scripts em Python para validação e segregação de dados na camada de ingestão e o Snowflake Data Cloud para armazenamento analítico, modelagem dimensional e observabilidade contínua de acordos de nível de serviço (SLAs) de qualidade.

O objetivo central é impedir que dados inconsistentes cheguem à camada de consumo analítico, protegendo relatórios corporativos contra distorções e reduzindo custos computacionais associados a tratamentos tardios.

O Problema de Negócio:
Em arquiteturas analíticas convencionais, transações corrompidas — caracterizadas por identificadores nulos, dízimas decorrentes de ponto flutuante e valores financeiros negativos — frequentemente são carregadas diretamente no Data Warehouse. Esse cenário resulta em:

Métricas financeiras e de faturamento distorcidas em painéis executivos e de Business Intelligence.

Consumo ineficiente de recursos computacionais para reprocessamentos e limpezas corretivas no banco de dados.

Falta de visibilidade forense sobre a origem das falhas nos sistemas emissores.

Este pipeline resolve o problema na raiz por meio de uma barreira técnica na esteira de extração e transformação, bifurcando registros conformes e inconsistentes antes da persistência definitiva.

Arquitetura da Solução e Estrutura de Dados:
O fluxo de dados é estruturado em três etapas principais:

Ingestão e Validação na Borda (Python e Pandas):
O script de validação aplica testes booleanos determinísticos sobre o lote bruto de dados. São verificadas a obrigatoriedade da chave primária (ID_TRANSACAO não nulo) e a validade da métrica de receita (VALOR_BRUTO estritamente maior que zero). Strings de categorias e sistemas emissores são padronizadas para eliminar duplicações semânticas.

Segregação em Duas Camadas no Snowflake:

Camada Confiável (TRUSTED_DATA): Armazena a tabela de fatos FATO_TRANSACAO_PADRONIZADA, contendo apenas dados aprovados. A modelagem adota precisão contábil com o tipo de dado NUMBER(12, 2) e neutralização temporal com TIMESTAMP_NTZ. Os atributos descritivos atuam como dimensões degeneradas persistidas na própria fato para acelerar agregações analíticas.

Camada de Quarentena (DATA_QUALITY_METRICS): Armazena a tabela de log LOG_ANOMALIAS_DADOS, estruturada como uma Dead Letter Queue (DLQ). Cada registro rejeitado retém o sistema de origem e o motivo detalhado da anomalia (como ID_NULO ou VALOR_NEGATIVO_OU_ZERO) para diagnóstico e auditoria.

Camada Semântica e Observabilidade:
Uma View analítica (VW_RESUMO_GOVERNANCA_DADOS) consolida os totais de registros conformes e quarentenados por meio de Common Table Expressions (CTEs), calculando indicadores em tempo real, como taxa de conformidade percentual, taxa de erro e volume financeiro protegido.

Métricas e Resultados Obtidos
A validação sobre o lote processado demonstrou a eficiência do modelo:

Não-contaminação financeira de 100% na camada analítica confiável (ausência de valores menores ou iguais a zero).

Eliminação total de identificadores nulos nas tabelas de fatos disponibilizadas para consumo.

Monitoramento contínuo da taxa de conformidade e segregação visual dos sistemas emissores com maior índice de anomalias (CRM, Portal Web e ERP).

Tecnologias e Ferramentas
Python 3 (Pandas e NumPy)

Snowflake Data Cloud (DDL, DML, CTEs e Views Semânticas)

SQL ANSI

Modelagem Dimensional (Tabela Fato Transacional com dimensões degeneradas)

Estrutura do Repositório
sql/ddl_tabelas.sql: Definição dos schemas, tabelas físicas e restrições de tipagem no Snowflake.

sql/auditoria_qualidade.sql: Construção da View analítica de governança utilizando CTEs.

sql/erros_por_origem.sql: Consulta de agregação para identificação de causa-raiz por sistema de origem.

sql/analise_vendas.sql: Consultas analíticas para extração de métricas de negócio na camada confiável.

src/pipeline.py: Script em Python responsável pela geração do lote sintético, validação de regras e separação física dos conjuntos de dados.

requirements.txt: Lista de dependências Python para reprodução do ambiente.

README.md: Documentação técnica do projeto.

Como Reproduzir o Projeto
Clonar o repositório:
git clone https://github.com/[seu-usuario]/[seu-repositorio].git
cd [seu-repositorio]

Instalar as dependências necessárias:
pip install -r requirements.txt

Executar o pipeline de validação:
python src/pipeline.py

Executar os scripts no Snowflake:

Executar os comandos de criação de objetos contidos na pasta sql na interface do Snowflake.

Carregar os arquivos gerados nas respectivas tabelas de destino.

Consultar a View DATA_QUALITY_METRICS.VW_RESUMO_GOVERNANCA_DADOS para validação dos indicadores de qualidade.