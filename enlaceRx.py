#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada de Enlace - Sub-camada de RECEPÇÃO (RX)
#
# Esta classe implementa um "produtor/consumidor" simples:
#   - Uma THREAD dedicada fica lendo continuamente a porta serial (via
#     objeto 'fisica') e empilhando os bytes recebidos em um buffer interno.
#   - O restante do programa (camada de aplicação) consome esse buffer
#     através dos métodos públicos (getBuffer, getNData, etc.), sem precisar
#     se preocupar com o timing da UART.
#####################################################
# Importa pacote de tempo
import time
# Threads (permite ler a UART em paralelo com o resto do programa)
import threading

# RX (UART)
class RX(object):

    def __init__(self, fisica):
        # Referência ao objeto da camada física (quem realmente fala com a UART)
        self.fisica      = fisica
        # Buffer interno onde os bytes recebidos vão se acumulando
        self.buffer      = bytes(bytearray())
        # Flag que, quando True, encerra o laço da thread (thread.py "kill switch")
        self.threadStop  = False
        # Flag que liga/desliga a leitura da UART sem matar a thread
        # (True = pode ler; False = leitura pausada)
        self.threadMutex = True
        # Quantidade máxima de bytes lidos por vez da porta serial
        self.READLEN     = 1024

    def thread(self): 
        # Laço principal executado em uma thread separada.
        # Fica rodando até que threadStop seja setado como True.
        while not self.threadStop:
            # Só lê da UART se a thread RX estiver "liberada" (threadMutex == True)
            if(self.threadMutex == True):
                # Lê até READLEN bytes da porta UART (via camada física)
                # rxTemp = dados lidos, nRx = quantidade de bytes lidos
                rxTemp, nRx = self.fisica.read(self.READLEN)
                # Se realmente vieram dados, concatena ao buffer acumulado
                if (nRx > 0):
                    self.buffer += rxTemp  
                # Pequena pausa para não sobrecarregar a CPU (polling)
                time.sleep(0.01)

    def threadStart(self):  
        # Cria e inicia a thread de recepção, que passa a rodar em paralelo
        # executando o método 'thread' definido acima
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        # Sinaliza para a thread encerrar seu laço (efeito contrário de threadStart)
        self.threadStop = True

    def threadPause(self):
        # Garante comunicacao Unidirecional (Start padrão c/ User On)
        self.threadMutex = False

    def threadResume(self):
        # Retoma a leitura da UART (efeito contrário de threadPause)
        self.threadMutex = True

    def getIsEmpty(self):
        # Verifica se o buffer RX está vazio (não usado ainda no projeto)
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    def getBufferLen(self):
         # Retorna quantos bytes estão atualmente armazenados no buffer RX
        return(len(self.buffer))

    def getAllBuffer(self, len):
        # Retorna todoo o conteúdo do buffer RX e em seguida o esvazia.
        # Pausa a thread durante a operação para evitar que novos dados
        # cheguem no meio da cópia (não usado ainda no projeto)
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    def getBuffer(self, nData):
        # Retorna apenas 'nData' bytes do início do buffer RX e os remove dele.
        # Pausa a thread durante a operação para evitar condição de corrida
        # (thread escrevendo no buffer enquanto ele é fatiado aqui)
        self.threadPause()
        # Separa os primeiros nData bytes...
        b           = self.buffer[0:nData]
        # ...e mantém no buffer apenas o que sobrou
        self.buffer = self.buffer[nData:]
        self.threadResume()
        return(b)

    def getNData(self, size):
        # Espera (bloqueando) até que o buffer RX acumule pelo menos 'size' bytes. 
        # Futuro bug: se a origem nunca enviar 'size' bytes, este laço fica preso aqui indefinidamente (sem timeout).
        while(self.getBufferLen() < size):
            time.sleep(0.05)                 
        # Quando a quantidade esperada chegou, retorna exatamente 'size' bytes
        return(self.getBuffer(size))


    def clearBuffer(self):
        # Esvazia completamente o buffer RX
        self.buffer = b""


