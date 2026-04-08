import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/script_to_voice_screen.dart';
import 'screens/voice_training_screen.dart';
import 'screens/pipeline_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // await Firebase.initializeApp(); // Initialize Firebase in production
  runApp(const ThtwaatApp());
}

class ThtwaatApp extends StatelessWidget {
  const ThtwaatApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Thtwaat AI Voice',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF121212),
        useMaterial3: true,
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/home': (context) => const ScriptToVoiceScreen(),
        '/training': (context) => const VoiceTrainingScreen(),
        '/pipeline': (context) => const PipelineScreen(),
      },
    );
  }
}
