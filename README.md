# dgraphs-report-with-grafana

Oracle Commerce MDEX Dgraphs reports with grafana. With python, information is sought in the xml of the dgraph, sent to BD influx and assembled as a base report in Grafana.

Relatórios Oracle Commerce MDEX Dgraphs usando influx e grafana. Desenvolvido script em python, as informações são buscadas no xml do dgraph, enviadas ao BD influx e montadas um dashboard de histórico e performance no Grafana.

#Dependencias

@

pip install -r requirements.txt

 #pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests
 #pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sshtunnel

 -subir localmente uma imagem docker usando influx e grafana