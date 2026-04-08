import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ScriptToVoiceScreen extends StatefulWidget {
  const ScriptToVoiceScreen({super.key});

  @override
  State<ScriptToVoiceScreen> createState() => _ScriptToVoiceScreenState();
}

class _ScriptToVoiceScreenState extends State<ScriptToVoiceScreen> {
  final TextEditingController _scriptController = TextEditingController();
  bool _isGenerating = false;
  String? _generatedAudioUrl;

  Future<void> _generateVoice() async {
    if (_scriptController.text.trim().isEmpty) return;

    setState(() => _isGenerating = true);
    try {
      final response = await apiService.generateVoice(_scriptController.text);
      setState(() {
        _generatedAudioUrl = response['data']['audioUrl']; // Placeholder URL back from backend
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Voice Generated Successfully!')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error generating voice: $e')));
      }
    } finally {
      if (mounted) setState(() => _isGenerating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Generate Voice'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              // Navigate to history screen
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings_voice),
            onPressed: () {
              Navigator.pushNamed(context, '/training');
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _scriptController,
              maxLines: 8,
              decoration: const InputDecoration(
                hintText: 'Enter your video script here to clone...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            _isGenerating
                ? const CircularProgressIndicator()
                : ElevatedButton.icon(
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Generate Voiceover'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                      backgroundColor: Colors.deepPurpleAccent,
                      foregroundColor: Colors.white,
                    ),
                    onPressed: _generateVoice,
                  ),
            const SizedBox(height: 24),
            if (_generatedAudioUrl != null) ...[
              const Divider(),
              const SizedBox(height: 16),
              const Text('Generated Output:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              const SizedBox(height: 16),
              Card(
                child: ListTile(
                  leading: const Icon(Icons.library_music, color: Colors.deepPurpleAccent),
                  title: const Text('Thtwaat AI Voiceover'),
                  subtitle: const Text('Ready to play'),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.play_circle_fill, size: 36),
                        onPressed: () {
                          // Play audio logic using just_audio package
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Playing audio...')));
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.download),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Downloading MP3...')));
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}
