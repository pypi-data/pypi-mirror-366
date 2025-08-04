# beta-Cynosure
Aplicação para extrair dados Anuais e Trimestrais da CVM de todas as empresas.

Ele foi o rascunho para a aplicação com AI para obtenção, processamento, armazenamento, atualização e análise de dados.

## Funcionalidade
Baixa os dados anuais (DFP) e trimestrais (ITR) diretamente do portal da CVM.

Calcula o número de trimestre com base nas datas.

Gera relatórios financeiros das empresas selecionadas.
```
 DFP:
Contém os dados anuais

 ITR:
Dados trimestrais

 FRE:
Número de ações em circulação
```

## Como usar
Instale e use o comando b-cynosure acompanhado do ano de início - ano fim do período, para baixar os demonstrativos de todas as empresas no período.

```
b-cynosure 2020-2024
```

Ou especifique a(s) empresa(s) cujo demonstrativo deva ser baixado informando o ticker:
```
b-cynosure 2024 -p petr vale
```