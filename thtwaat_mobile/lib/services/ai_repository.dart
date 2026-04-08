import 'api_service.dart';

class AiRepository {
  // Full pipeline: research → script → voice
  static Future<Map<String, dynamic>> runPipeline(String topic, String language) async {
    // 1. Start job
    final job = await ApiService.startPipeline(topic, language: language);
    final jobId = job['job_id'] as String;

    // 2. Poll until done (max 3 min)
    for (int i = 0; i < 90; i++) {
      await Future.delayed(const Duration(seconds: 2));
      final status = await ApiService.pipelineStatus(jobId);
      if (status['status'] == 'done') return status;
      if (status['status'] == 'error') throw Exception(status['detail']);
    }
    throw Exception('Pipeline timeout');
  }
}
