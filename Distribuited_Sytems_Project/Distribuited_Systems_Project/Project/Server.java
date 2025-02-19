import java.io.*;
import java.net.*;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.Semaphore;
import java.util.HashMap;
import java.util.Map;

public class Server {
    public static final int MAX_CLIENTS =5;
    private static final int PORT = 12345;

    public static void main(String[] args) {
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Servidor iniciado na porta " + PORT);

            // Gerir servidor
            ServerManager serverManager = new ServerManager(MAX_CLIENTS);

            while (true) {
                Socket socket = serverSocket.accept();
                System.out.println("Novo cliente conectado");

                Thread clientThread = new Thread(new ServerWorker(socket, serverManager));
                clientThread.start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

class ServerWorker implements Runnable {
    private final Socket socket;
    private final DataInputStream input;
    private final DataOutputStream output;
    private final ServerManager serverManager;

    public ServerWorker(Socket socket, ServerManager serverManager) {
        this.socket = socket;
        this.serverManager = serverManager;
        try {
            this.input = new DataInputStream(socket.getInputStream());
            this.output = new DataOutputStream(socket.getOutputStream());
        } catch (IOException e) {
            throw new RuntimeException("Erro ao inicializar streams", e);
        }
    }

    @Override
    public void run() {
        try {
            serverManager.acquireSession();
            System.out.println("Sessão adquirida. Sessões ativas: " + serverManager.getActiveSessions());

            boolean running = true;

            while (running) {
                int command = input.readByte();

                switch (command) {
                    case 1: // Registro
                        String regUsername = input.readUTF();
                        String regPassword = input.readUTF();
                        output.writeUTF(serverManager.registerUser(regUsername, regPassword));
                        output.flush();
                        break;

                    case 2: // Login
                        String loginUsername = input.readUTF();
                        String loginPassword = input.readUTF();
                        output.writeUTF(serverManager.loginUser(loginUsername, loginPassword));
                        output.flush();
                        break;

                    case 3: // PUT
                        String key = input.readUTF();
                        String value = input.readUTF();
                        output.writeUTF(serverManager.putValue(key, value));
                        output.flush();
                        break;

                    case 4: // GET
                        String keyToGet = input.readUTF();
                        String result = serverManager.getValue(keyToGet);
                        if (result != null) {
                            output.writeBoolean(true);
                            output.writeUTF(result);
                        } else {
                            output.writeBoolean(false);
                        }
                        output.flush();
                        break;

                    case 5: // multiPut
                        int pairCount = input.readInt(); // Número de pares chave-valor
                        Map<String, byte[]> pairs = new HashMap<>();
                        for (int i = 0; i < pairCount; i++) {
                            String multiPutKey = input.readUTF();
                            int valueSize = input.readInt();
                            byte[] valueBytes = new byte[valueSize];
                            input.readFully(valueBytes);
                            pairs.put(multiPutKey, valueBytes);
                        }
                        serverManager.multiPut(pairs);
                        output.writeUTF("multiPut executado com sucesso.");
                        output.flush();
                        break;

                    case 6: // multiGet
                        int keyCount = input.readInt(); // Número de chaves
                        Set<String> keys = new HashSet<>();
                        for (int i = 0; i < keyCount; i++) {
                            keys.add(input.readUTF());
                        }
                        Map<String, byte[]> resultMap = serverManager.multiGet(keys);
                        output.writeInt(resultMap.size());
                        for (Map.Entry<String, byte[]> entry : resultMap.entrySet()) {
                            output.writeUTF(entry.getKey());
                            output.writeInt(entry.getValue().length);
                            output.write(entry.getValue());
                        }
                        output.flush();
                        break;

                    case 0: // Encerrar conexão
                        running = false;
                        System.out.println("Cliente desconectado. Sessão ficará livre.");
                        break;

                    default:
                        output.writeUTF("Comando inválido.");
                        output.flush();
                        break;
                }
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            serverManager.releaseSession();
            try {
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
