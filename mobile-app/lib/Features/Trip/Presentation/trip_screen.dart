import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TripScreen extends StatefulWidget {
  const TripScreen({super.key});

  @override
  State<TripScreen> createState() => _TripScreenState();
}

class _TripScreenState extends State<TripScreen> {
  final _storage = const FlutterSecureStorage();
  List<dynamic> _tasks = [];
  bool _isLoading = true;
  Timer? _pollingTimer;
  String? _activeTripId;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  @override
  void dispose() {
    _pollingTimer?.cancel(); // Stop polling when driver leaves screen
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    await _fetchActiveTrip();
    // Poll every 30s with Timer.periodic
    _pollingTimer = Timer.periodic(const Duration(seconds: 30), (_) => _fetchTasks());
  }

  // TASK: GET /api/v1/trips?status=active
  Future<void> _fetchActiveTrip() async {
    try {
      String? token = await _storage.read(key: 'jwt_token');
      final response = await http.get(
        Uri.parse('https://your-api.com/api/v1/trips?status=active'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final List trips = json.decode(response.body);
        if (trips.isNotEmpty) {
          _activeTripId = trips[0]['id'].toString();
          await _fetchTasks();
        }
      }
    } catch (e) {
      debugPrint("Error fetching active trip: $e");
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // TASK: GET /api/v1/tasks?trip_id={id}
  Future<void> _fetchTasks() async {
    if (_activeTripId == null) return;

    try {
      String? token = await _storage.read(key: 'jwt_token');
      final response = await http.get(
        Uri.parse('https://your-api.com/api/v1/tasks?trip_id=$_activeTripId'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        List fetchedTasks = json.decode(response.body);
        // Returns stops ordered by sequence_order
        fetchedTasks.sort((a, b) => a['sequence_order'].compareTo(b['sequence_order']));
        
        setState(() => _tasks = fetchedTasks);
      }
    } catch (e) {
      debugPrint("Polling error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    int completedCount = _tasks.where((t) => t['status'] == 'completed').length;

    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      appBar: AppBar(title: const Text("Active Trip"), backgroundColor: Colors.black),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Progress HUD (e.g. '3/7 stops completed')
                Container(
                  padding: const EdgeInsets.all(16),
                  color: Colors.blueAccent.withOpacity(0.1),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text("Trip Progress", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      Text("$completedCount / ${_tasks.length} stops completed", 
                           style: const TextStyle(color: Colors.blueAccent)),
                    ],
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: _tasks.length,
                    itemBuilder: (context, index) {
                      final task = _tasks[index];
                      return ListTile(
                        leading: CircleAvatar(child: Text("${task['sequence_order']}")),
                        title: Text(task['address'] ?? 'Unknown Address', style: const TextStyle(color: Colors.white)),
                        subtitle: Text("Status: ${task['status']}", style: const TextStyle(color: Colors.grey)),
                        trailing: Icon(
                          task['status'] == 'completed' ? Icons.check_circle : Icons.pending,
                          color: task['status'] == 'completed' ? Colors.green : Colors.grey,
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
    );
  }
}