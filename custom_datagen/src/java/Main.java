

import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.glassfish.tyrus.client.ClientManager;

import jakarta.websocket.EncodeException;
import jakarta.websocket.Endpoint;
import jakarta.websocket.EndpointConfig;
import jakarta.websocket.Session;

class WebSocketClient {
    private static ClientManager client;
    public WebSocketClient() {
        client = ClientManager.createClient();
    }

    public void sendNotification(String wsUrl, DataGenerationNotification notification) {
        try {
            Session session = client.connectToServer(new Endpoint() {
                @Override
                public void onOpen(Session session, EndpointConfig config) {
                    try {
                        // Send the notification
                        session.getBasicRemote().sendObject(notification);
                    } catch (EncodeException | IOException e) {
                        e.printStackTrace();
                    }
                }
            }, URI.create(wsUrl));
            session.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

public class Main {
    private static final int BLOCKSIZE = 50_000;
    
    public static void main(String[] args) throws InterruptedException {
        WebSocketClient wsClient = new WebSocketClient();
        ExecutorService threadPool = Executors.newVirtualThreadPerTaskExecutor();
        while (true) {
            List<Long> data = new ArrayList<>(BLOCKSIZE);
            for (int i = 0; i < BLOCKSIZE; i++) {
                data.set(i, 1L);
            }
            DataTransportType transport = DataTransportType.newBuilder()
                .setDataList(data)
                .build();
            DataGenerationNotification notification = DataGenerationNotification.newBuilder()
                .setData(transport)
                .setId("test")
                .build();
            Runnable r = () -> wsClient.sendNotification("ws://localhost:3000", notification);
            threadPool.execute(r);
            Thread.sleep(1L);
        }
    }
}