#!/usr/bin/env python3
# -*- coding: utf-8 -*-
####################################################
# Classe "fachada" (facade): junta a camada física (fisica) com as duas
# sub-camadas de enlace (RX e TX), oferecendo para a aplicação uma
# interface simples: enable(), disable(), sendData() e getData().
####################################################

# Importa pacote de tempo
import time

# Interface Física (quem fala diretamente com a porta serial)
from interfaceFisica import fisica

# Enlace Tx e Enlace Rx (sub-camadas de transmissão e recepção)
from enlaceRx import RX
from enlaceTx import TX

class enlace(object):
    
    def __init__(self, name):
        # Camada Física de Comunicação e Sub-cmadas RX e TX
        self.fisica      = fisica(name)
        self.rx          = RX(self.fisica)
        self.tx          = TX(self.fisica)
        # Estado da conexão (não usado ainda)
        self.connected   = False

    def enable(self):
        # Abre a porta serial e inicia as threads RX e TX,
        # deixando a comunicação pronta para uso
        self.fisica.open()
        self.rx.threadStart()
        self.tx.threadStart()

    def disable(self):
        # Desativa Thread RX, Thread TX e Comunicacao Serial
        self.rx.threadKill()
        self.tx.threadKill()
        time.sleep(1)
        self.fisica.close()

    def sendData(self, data):
        # Envia 'data' para o buffer TX; a thread TX cuida de
        # efetivamente escrever esses bytes na UART
        self.tx.sendBuffer(data)
        
    def getData(self, size):
        # Bloqueia até que 'size' bytes estejam disponíveis no buffer RX
        # e então os retorna, junto com a quantidade lida
        data = self.rx.getNData(size)
        return(data, len(data))
