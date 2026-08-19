#####################################################
# Camada Física da Computação # APS 2
####################################################
from enlace import *
import time
import numpy as np
import random
import struct

# Main
def main():
    try:
        # -- COMUNICAÇÃO --
        # ESTABELECER
        print("Iniciou o main")
        serialName = "COM7" 
        com1 = enlace(serialName)
        com1.enable()
        print("Abriu a comunicação")

        # DADOS
        txBuffer = []
        numeros = []
        n_numbers = np.random.randint(5, 16)

        for _ in range(n_numbers):
            numero = np.float32(np.random.uniform(-1000, 1000))
            numeros.append(numero)
            txBuffer.extend(numero.tobytes())

        txBuffer = np.asarray(txBuffer, dtype=np.uint8)

        print("Quantidade de números:", n_numbers)
        print("Números enviados:", numeros)
        print("Soma esperada:", np.sum(numeros))
        print("Tamanho Dados:", len(txBuffer), "bytes")

        # ENVIO
        # Envio via EnlaceTX
        com1.sendData(txBuffer)

        # Checagem
        while com1.tx.threadMutex:
            time.sleep(0.01)
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))

        # RECEBIMENTO
        print("Aguardando resposta do servidor...")
        # Timeout Server
        tempo_inicio = time.time()
        while com1.rx.getBufferLen() == 0:
            if time.time() - tempo_inicio > 5:
                print("Timeout: nenhum dado recebido em 5 segundos")
                return
            time.sleep(0.01)
        # Dados
        rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
        print("recebeu {} bytes".format(len(rxBuffer)))

        # VALIDACAO
        # Tamanho (1 float32)
        if len(rxBuffer) != 4:
            print("ERRO: servidor deveria enviar exatamente 4 bytes.")
            print("Valor esperado:", 4)
            print("Valor recebido:", len(rxBuffer))
        else:
        # Soma
            valor_recebido = np.frombuffer(bytes(rxBuffer), dtype=np.float32)[0]
            print("Valor recebido:", valor_recebido)
            soma = np.sum(numeros)
            if np.isclose(valor_recebido, soma):
                print("OK: o valor recebido equivale à soma dos números.")
            else:
                print("ERRO: o valor recebido NÃO equivale à soma.")
                print("Valor esperado:", soma)
                print("Valor recebido:", valor_recebido)

        # ENCERRAR
        print("Comunicação encerrada")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
if __name__ == "__main__":
    main()
