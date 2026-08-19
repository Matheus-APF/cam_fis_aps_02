#!/usr/bin/env python3
# -*- coding: utf-8 -*-
####################################################
# Camada de Enlace - Sub-camada de TRANSMISSÃO (TX)
#
# Funciona de forma "espelhada" à classe RX: uma thread fica dormente,
# esperando alguém chamar sendBuffer(). Quando isso acontece, a thread
# "acorda" (threadMutex vira True), escreve os dados na UART através do
# objeto 'fisica' e volta a dormir (threadMutex volta a False).
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# TX (User)
class TX(object):
 
    def __init__(self, fisica):
        # Referência ao objeto da camada física (quem realmente escreve na UART)
        self.fisica      = fisica
        # Buffer local com os dados a serem transmitidos
        self.buffer      = bytes(bytearray())
        # Quantidade de bytes efetivamente transmitidos na última escrita
        self.transLen    = 0
        # Indica se o buffer TX está vazio (não usado ainda no projeto)
        self.empty       = True
        # Flag que funciona como "gatilho": quando True, a thread deve
        # escrever o buffer atual na UART
        self.threadMutex = False
        # Flag que, quando True, encerra o laço da thread
        self.threadStop  = False


    def thread(self):
        # Laço principal executado em uma thread separada, enquanto a
        # comunicação estiver ativa (threadStop == False)
        while not self.threadStop:
            # Só escreve na UART quando threadMutex for acionado (True),
            # ou seja, quando sendBuffer() tiver sido chamado
            if(self.threadMutex):
                # Escreve o conteúdo do buffer na porta física e guarda
                # quantos bytes foram efetivamente transmitidos
                self.transLen    = self.fisica.write(self.buffer)
                # Volta a "dormir": libera a thread para aguardar o próximo envio
                self.threadMutex = False

    def threadStart(self):
        # Cria e inicia a thread de transmissão em paralelo
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        # Sinaliza para a thread encerrar seu laço (efeito contrário de threadStart)
        self.threadStop = True

    def threadPause(self):
        # Pausa a transmissão (impede a thread de escrever na UART)
        self.threadMutex = False

    def threadResume(self):
        # Retoma a transmissão (efeito contrário de threadPause)
        self.threadMutex = True

    def sendBuffer(self, data):
        # Recebe os dados a transmitir, guarda no buffer local e "aciona"
        # a thread TX (threadMutex = True) para que ela escreva na UART
        self.transLen = 0
        self.buffer = data
        self.threadMutex  = True

    def getBufferLen(self):
        # Retorna o tamanho (em bytes) dos dados atualmente no buffer TX
        return(len(self.buffer))

    def getStatus(self):
        # Retorna quantos bytes foram efetivamente transmitidos na última
        # escrita (resultado de fisica.write, já convertido para nº de bytes
        # originais, não de caracteres hexadecimais)
        return(self.transLen)
        

    def getIsBussy(self):
        # Indica se a thread TX ainda está com uma transmissão pendente/ativa
        return(self.threadMutex)