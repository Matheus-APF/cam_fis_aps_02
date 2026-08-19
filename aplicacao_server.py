#####################################################
# Camada Física da Computação # APS 2
#####################################################
from enlace import *
import time
import numpy as np


# Main
def main():
    try:
        # -- COMUNICAÇÃO --
        # ESTABELECER
        print("Iniciou o main")
        serialName = "COM8"   # Ajustar para a porta do servidor
        com1 = enlace(serialName)
        com1.enable()
        print("Abriu a comunicação")


        # RECEBIMENTO
        print("Aguardando dados do cliente...")

        # Aguarda indefinidamente o primeiro dado
        while com1.rx.getBufferLen() == 0:
            time.sleep(0.01)

        print("Primeiro dado recebido")

        rxBuffer = bytearray()
        tempo_inicio = time.time()

        while True:

            tamanho_atual = com1.rx.getBufferLen()

            if tamanho_atual > 0:

                dados, nRx = com1.getData(tamanho_atual)
                rxBuffer.extend(dados)

                # Reinicia timeout sempre que chegam dados
                tempo_inicio = time.time()

                # Verifica marcador de fim: 4 bytes iguais a 1
                if len(rxBuffer) >= 4 and rxBuffer[-4:] == bytearray([1, 1, 1, 1]):

                    print("Marcador de fim detectado")

                    # Remove o marcador para não ser interpretado como float
                    rxBuffer = rxBuffer[:-4]

                    break

            # Timeout continua existindo apenas como segurança
            if time.time() - tempo_inicio > 1:
                print("Timeout de recepção")
                break

            time.sleep(0.01)

        print("recebeu {} bytes".format(len(rxBuffer)))

        # DADOS
        rxBuffer, nRx = com1.getData(com1.rx.getBufferLen())
        print("recebeu {} bytes".format(len(rxBuffer)))

        # VALIDACAO
        # Cada float32 deve ocupar exatamente 4 bytes
        if len(rxBuffer) % 4 != 0:
            print("ERRO: quantidade de bytes recebida inválida.")
            print("Cada número deve possuir 4 bytes.")
        else:
            quantidade = len(rxBuffer) // 4
            print("Quantidade de números recebidos:", quantidade)

            # Verifica requisito da atividade: entre 5 e 15 números
            if quantidade < 5 or quantidade > 15:
                print("ERRO: quantidade de números inválida.")
                print("Esperado: entre 5 e 15 números.")
            else:
                # Converte todos os bytes recebidos para float32
                numeros = np.frombuffer(bytes(rxBuffer),dtype=np.float32)
                print("Números recebidos:", numeros)

                # SOMA
                soma = np.float32(np.sum(numeros))
                print("Soma:", soma)

                # ENVIO
                # Um float32 = exatamente 4 bytes
                txBuffer = np.asarray(bytearray(soma.tobytes()),dtype=np.uint8)
                print("Tamanho resposta:", len(txBuffer), "bytes")
                com1.sendData(txBuffer)
                # Checagem
                while com1.tx.threadMutex:
                    time.sleep(0.01)
                txSize = com1.tx.getStatus()
                print("enviou = {}".format(txSize))

        # ENCERRAR
        print("Comunicação encerrada")
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

if __name__ == "__main__":
    main()