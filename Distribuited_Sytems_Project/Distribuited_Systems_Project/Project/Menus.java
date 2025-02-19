class Menus {
    public static void mainMenu() {
        System.out.println("1-> Registo");
        System.out.println("2-> Login");
        System.out.println("4-> Sair");
        System.out.print("Opção: ");
    }

    public static void afterLoginMenu() {
        System.out.println("1-> PUT (inserir/atualizar chave-valor)");
        System.out.println("2-> GET (consulta do valor por chave)");
        System.out.println("3-> multiPut (inserir múltiplos pares chave-valor)");
        System.out.println("4-> multiGet (consultar múltiplas chaves)");
        System.out.println("5-> Log Out");
        System.out.print("Opção: ");
    }
}
