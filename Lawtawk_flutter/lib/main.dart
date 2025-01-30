import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const LawTawkApp());
}

class LawTawkApp extends StatelessWidget {
  const LawTawkApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LawTawk? - The Constitutional Companion',
      theme: ThemeData.light().copyWith(
        primaryColor: Colors.blueAccent,
        colorScheme: ColorScheme.light().copyWith(
          secondary: Colors.blueAccent,
        ),
        scaffoldBackgroundColor: Colors.white,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.blueAccent,
          titleTextStyle: TextStyle(color: Colors.white, fontSize: 22),
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Colors.black87),
        ),
      ),
      darkTheme: ThemeData.dark().copyWith(
        primaryColor: Colors.blueAccent,
        colorScheme: ColorScheme.dark().copyWith(
          secondary: Colors.blueAccent,
        ),
        scaffoldBackgroundColor: Colors.black87,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.blueAccent,
          titleTextStyle: TextStyle(color: Colors.white, fontSize: 22),
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Colors.white70),
        ),
      ),
      themeMode: ThemeMode.system,
      home: const SplashScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Map<String, String>> _messages = [];
  final TextEditingController _controller = TextEditingController();

  bool _isListening = false;

  @override
  void initState() {
    super.initState();
  }

  Future<void> _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;

    final userMessage = _controller.text.trim();

    // Add user message to the chat
    setState(() {
      _messages.add({'sender': 'You', 'message': userMessage});
    });

    // Send the message to the Flask backend
    final response = await _sendMessageToBackend(userMessage);

    setState(() {
      _messages.add({'sender': 'Bot', 'message': response});
    });

    _controller.clear();
  }

  Future<String> _sendMessageToBackend(String userMessage) async {
    final url = Uri.parse('http://<YOUR_BACKEND_URL>/chat');  // Replace with your Flask API URL
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'user_input': userMessage}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['response'];
    } else {
      throw Exception('Failed to get response from the backend');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.blueAccent,
        title: const Text('LawTawk ?'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['sender'] == 'You';

                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 5, horizontal: 10),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.blueAccent : Colors.grey[200],
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      message['message']!,
                      style: TextStyle(
                        color: isUser ? Colors.white : Colors.black87,
                        fontSize: 16,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Ask something about the Constitution...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 15),
                    ),
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  color: Colors.blueAccent,
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
