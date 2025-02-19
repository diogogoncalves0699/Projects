import java.io.*;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Scanner;

public class MenuHandler {
    private final DataInputStream input;
    private final DataOutputStream output;
    private final Scanner scanner;

    public MenuHandler(DataInputStream input, DataOutputStream output, Scanner scanner) {
        this.input = input;
        this.output = output;
        this.scanner = scanner;
    }

    public void start() {
        boolean running = true;
        boolean loggedIn = false;

        while (running) {
            if (!loggedIn) {
                Menus.mainMenu();
                int choice = scanner.nextInt();
                scanner.nextLine(); 

                switch (choice) {
                    case 1: // Registar
                        register();
                        break;
                    case 2: // Login
                        loggedIn = login(); // Verifica se o login foi bem-sucedido
                        if (loggedIn) {
                            System.out.println("Login bem-sucedido. A mudar para o menu pós-login.");
                        } else {
                            System.out.println("Falha no login. Retornar ao menu principal.");
                        }
                        break;
                    case 4: // Sair
                        running = false;
                        System.out.println("Encerrar cliente.");
                        break;
                    default:
                        System.out.println("Opção inválida!");
                        break;
                }
            } else {
                Menus.afterLoginMenu();
                int choice = scanner.nextInt();
                scanner.nextLine(); 

                switch (choice) {
                    case 1: // PUT
                        put();
                        break;
                    case 2: // GET
                        get();
                        break;
                    case 3: // multiPut
                        multiPut();
                        break;
                    case 4: // multiGet
                        multiGet();
                        break;
                    case 5: // Log Out
                        try {
                            output.writeByte(0); // Código para encerrar conexão
                            output.flush();
                            loggedIn = false;
                            System.out.println("Encerrar com êxito.");
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        break;
                    default:
                        System.out.println("Opção inválida!");
                        break;
                }
            }
        }
    }



    private void register() {
        try {
            System.out.print("Insira o nome de utilizador: ");
            String username = scanner.nextLine();

            System.out.print("Insira a palavra-passe: ");
            String password = scanner.nextLine();

            output.writeByte(1);
            output.writeUTF(username);
            output.writeUTF(password);

            System.out.println(input.readUTF());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private boolean login() {
        try {
            System.out.print("Insira o nome de utilizador: ");
            String username = scanner.nextLine();

            System.out.print("Insira a palavra-passe: ");
            String password = scanner.nextLine();

            output.writeByte(2); // Código para login
            output.writeUTF(username);
            output.writeUTF(password);
            output.flush(); // Garante envio imediato

            String response = input.readUTF();
            System.out.println("Resposta do servidor: " + response);

            return response.equals("Autenticação bem-sucedida.");
        } catch (IOException e) {
            e.printStackTrace();
        }
        return false;
    }


    private void put() {
        try {
            System.out.print("Introduza a chave: ");
            String key = scanner.nextLine();

            System.out.print("Introduza o valor: ");
            String value = scanner.nextLine();

            output.writeByte(3);
            output.writeUTF(key);
            output.writeUTF(value);

            System.out.println(input.readUTF());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void get() {
        try {
            System.out.print("Introduza a chave: ");
            String key = scanner.nextLine();

            output.writeByte(4);
            output.writeUTF(key);

            boolean found = input.readBoolean();
            if (found) {
                String value = input.readUTF();
                System.out.println("Valor: " + value);
            } else {
                System.out.println("Chave não encontrada.");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void multiPut() {
        try {
            System.out.print("Número de pares chave-valor a inserir: ");
            int count = scanner.nextInt();
            scanner.nextLine(); 

            Map<String, byte[]> pairs = new HashMap<>();
            for (int i = 0; i < count; i++) {
                System.out.print("Chave: ");
                String key = scanner.nextLine();
                System.out.print("Valor: ");
                String value = scanner.nextLine();
                pairs.put(key, value.getBytes());
            }

            output.writeByte(5); // Código para multiPut
            output.writeInt(pairs.size());
            for (Map.Entry<String, byte[]> entry : pairs.entrySet()) {
                output.writeUTF(entry.getKey());
                output.writeInt(entry.getValue().length);
                output.write(entry.getValue());
            }

            System.out.println(input.readUTF());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void multiGet() {
        try {
            System.out.print("Número de chaves a consultar: ");
            int count = scanner.nextInt();
            scanner.nextLine(); 

            Set<String> keys = new HashSet<>();
            for (int i = 0; i < count; i++) {
                System.out.print("Chave: ");
                keys.add(scanner.nextLine());
            }

            output.writeByte(6); // Código para multiGet
            output.writeInt(keys.size());
            for (String key : keys) {
                output.writeUTF(key);
            }
            output.flush(); // Garante que os dados sejam enviados imediatamente

            int resultSize = input.readInt();
            System.out.println("Resultados:");
            for (int i = 0; i < resultSize; i++) {
                String key = input.readUTF();
                int valueSize = input.readInt();
                byte[] value = new byte[valueSize];
                input.readFully(value);
                System.out.println("Chave: " + key + ", Valor: " + new String(value));
            }

            // Pausa para aguardar o utilizador
            System.out.println("\nPressione qualquer tecla para voltar ao menu...");
            scanner.nextLine(); // Aguarda a entrada do utilizador
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
