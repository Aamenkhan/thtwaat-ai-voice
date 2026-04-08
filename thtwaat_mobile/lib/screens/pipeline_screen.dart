import 'package:flutter/material.dart';
import '../services/ai_repository.dart';

class PipelineScreen extends StatefulWidget {
  const PipelineScreen({super.key});
  @override
  State<PipelineScreen> createState() => _PipelineScreenState();
}

class _PipelineScreenState extends State<PipelineScreen> {
  final _ctrl = TextEditingController();
  String _lang = 'ar';
  bool _loading = false;
  String _step = '';
  Map<String, dynamic>? _result;
  String? _error;

  Future<void> _run() async {
    if (_ctrl.text.trim().isEmpty) return;
    setState(() { _loading = true; _error = null; _result = null; _step = 'Starting…'; });
    try {
      final res = await AiRepository.runPipeline(_ctrl.text.trim(), _lang);
      setState(() { _result = res; });
    } catch (e) {
      setState(() { _error = e.toString(); });
    } finally {
      setState(() { _loading = false; _step = ''; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0f172a),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0f172a),
        title: const Text('AI Pipeline', style: TextStyle(color: Colors.white)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          TextField(
            controller: _ctrl,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Enter topic…',
              hintStyle: const TextStyle(color: Colors.white38),
              filled: true,
              fillColor: Colors.white10,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none),
            ),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _lang,
            dropdownColor: const Color(0xFF1e293b),
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(filled: true, fillColor: Colors.white10,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none)),
            items: const [
              DropdownMenuItem(value: 'ar', child: Text('Arabic')),
              DropdownMenuItem(value: 'en', child: Text('English')),
              DropdownMenuItem(value: 'hi', child: Text('Hindi')),
            ],
            onChanged: (v) => setState(() => _lang = v!),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loading ? null : _run,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF22c55e),
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: _loading
                ? const CircularProgressIndicator(color: Colors.white, strokeWidth: 2)
                : const Text('START PIPELINE', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 20),
          if (_loading && _step.isNotEmpty)
            Text(_step, style: const TextStyle(color: Colors.white54)),
          if (_error != null)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10)),
              child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ),
          if (_result != null) ...[
            const Text('Script:', style: TextStyle(color: Colors.white70, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Expanded(
              child: SingleChildScrollView(
                child: Text(_result!['script'] ?? '', style: const TextStyle(color: Colors.white60)),
              ),
            ),
          ],
        ]),
      ),
    );
  }
}
