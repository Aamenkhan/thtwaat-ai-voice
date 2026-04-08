import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'https://thtwaat-ai-voice.onrender.com';
  static const Duration _timeout = Duration(seconds: 60);

  static Map<String, String> get _headers => {'Content-Type': 'application/json'};

  static Future<Map<String, dynamic>> _get(String path) async {
    final res = await http.get(Uri.parse('$baseUrl$path'), headers: _headers).timeout(_timeout);
    return _parse(res);
  }

  static Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    final res = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
      body: jsonEncode(body),
    ).timeout(_timeout);
    return _parse(res);
  }

  static Map<String, dynamic> _parse(http.Response res) {
    final data = jsonDecode(res.body);
    if (res.statusCode >= 200 && res.statusCode < 300) return data;
    throw Exception(data['detail'] ?? 'Error ${res.statusCode}');
  }

  // Health check
  static Future<Map<String, dynamic>> health() => _get('/health');

  // Research
  static Future<Map<String, dynamic>> research(String topic, {String language = 'ar'}) =>
      _post('/api/research', {'topic': topic, 'language': language});

  // Script
  static Future<Map<String, dynamic>> generateScript(String researchData, {String style = 'educational'}) =>
      _post('/api/script', {'research_data': researchData, 'style': style});

  // Voice
  static Future<Map<String, dynamic>> generateVoice(String script, {String age = 'young_adult', String gender = 'neutral'}) =>
      _post('/api/voice', {'script': script, 'age': age, 'gender': gender, 'reduce_noise': true});

  // Full pipeline
  static Future<Map<String, dynamic>> startPipeline(String topic, {String language = 'ar'}) =>
      _post('/api/pipeline', {'topic': topic, 'language': language});

  static Future<Map<String, dynamic>> pipelineStatus(String jobId) => _get('/api/pipeline/$jobId');

  // Voice upload (multipart)
  static Future<Map<String, dynamic>> uploadVoice(String text, File audioFile) async {
    final req = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/generate'));
    req.fields['text'] = text;
    req.files.add(await http.MultipartFile.fromPath('voice', audioFile.path));
    final streamed = await req.send().timeout(_timeout);
    final res = await http.Response.fromStream(streamed);
    return _parse(res);
  }
}
