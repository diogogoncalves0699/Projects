import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class ServerManager {
    private final int maxClients;
    private int activeSessions;
    private final Lock sessionLock;
    private final Condition sessionCondition;
    private final Map<String, String> users;
    private final Map<String, String> keyValueStore;
    private final Lock usersLock;
    private final Lock keyValueLock;

    public ServerManager(int maxClients) {
        this.maxClients = maxClients;
        this.activeSessions = 0;
        this.sessionLock = new ReentrantLock();
        this.sessionCondition = sessionLock.newCondition();
        this.users = new HashMap<>();
        this.keyValueStore = new HashMap<>();
        this.usersLock = new ReentrantLock();
        this.keyValueLock = new ReentrantLock();
    }

    public void acquireSession() throws InterruptedException {
        sessionLock.lock();
        try {
            while (activeSessions >= maxClients) {
                System.out.println(Thread.currentThread().getName() + " aguardar a  disponibilidade de uma  sessão...");
                sessionCondition.await(); // Aguarda até que uma sessão seja liberada
            }
            activeSessions++;
            System.out.println(Thread.currentThread().getName() + "  Sessão adquirida. Sessões ativas: " + activeSessions);
        } finally {
            sessionLock.unlock();
        }
    }

    public void releaseSession() {
        sessionLock.lock();
        try {
            activeSessions--;
            System.out.println(Thread.currentThread().getName() + " Sessão livre . Sessões ativas: " + activeSessions);
            if (activeSessions < maxClients) {
                sessionCondition.signalAll();
            }
        } finally {
            sessionLock.unlock();
        }
    }

    public int getActiveSessions() {
        sessionLock.lock();
        try {
            return activeSessions;
        } finally {
            sessionLock.unlock();
        }
    }

    public String registerUser(String username, String password) {
        usersLock.lock();
        try {
            if (users.containsKey(username)) {
                return "Utilizador já existe.";
            }
            users.put(username, password);
            return "Registro bem-sucedido.";
        } finally {
            usersLock.unlock();
        }
    }

    public String loginUser(String username, String password) {
        usersLock.lock();
        try {
            if (users.containsKey(username) && users.get(username).equals(password)) {
                return "Autenticação bem-sucedida.";
            }
            return "Nome de utilizador ou senha inválidos.";
        } finally {
            usersLock.unlock();
        }
    }

    public String putValue(String key, String value) {
        keyValueLock.lock();
        try {
            keyValueStore.put(key, value);
            return "Chave-valor inserido/atualizado com sucesso.";
        } finally {
            keyValueLock.unlock();
        }
    }

    public String getValue(String key) {
        keyValueLock.lock();
        try {
            return keyValueStore.getOrDefault(key, null);
        } finally {
            keyValueLock.unlock();
        }
    }

    public void multiPut(Map<String, byte[]> pairs) {
        keyValueLock.lock();
        try {
            for (Map.Entry<String, byte[]> entry : pairs.entrySet()) {
                keyValueStore.put(entry.getKey(), new String(entry.getValue())); 
            }
        } finally {
            keyValueLock.unlock();
        }
    }

    public Map<String, byte[]> multiGet(Set<String> keys) {
        keyValueLock.lock();
        try {
            Map<String, byte[]> result = new HashMap<>();
            for (String key : keys) {
                if (keyValueStore.containsKey(key)) {
                    result.put(key, keyValueStore.get(key).getBytes());
                }
            }
            return result;
        } finally {
            keyValueLock.unlock();
        }
    }
}
