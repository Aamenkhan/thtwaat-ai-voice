import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isLoading = false;

  Future<void> _signInDemo() async {
    setState(() => _isLoading = true);
    try {
      // In production, use FirebaseAuth to sign in, get the token:
      // final idToken = await user.getIdToken();
      // apiService.setToken(idToken!);
      
      apiService.setToken('demo_firebase_token_123'); // Demo Mode
      await apiService.login();
      
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Login failed: $e')));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.mic, size: 100, color: Colors.deepPurpleAccent),
              const SizedBox(height: 24),
              const Text('Thtwaat AI Voice', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              const Text('Clone your voice & generate audio instantly', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 48),
              _isLoading 
                  ? const CircularProgressIndicator()
                  : ElevatedButton.icon(
                      icon: const Icon(Icons.login),
                      label: const Text('Continue with Demo Login'),
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(double.infinity, 50),
                        backgroundColor: Colors.deepPurpleAccent,
                        foregroundColor: Colors.white,
                      ),
                      onPressed: _signInDemo,
                    )
            ],
          ),
        ),
      ),
    );
  }
}
