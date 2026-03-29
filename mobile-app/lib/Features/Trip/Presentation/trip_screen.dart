import 'package:flutter/material.dart';
import 'dart:async';
import '../../../services/api_service.dart';

class TripScreen extends StatefulWidget {
  final String tripId;
  const TripScreen({super.key, required this.tripId});

  @override
  State<TripScreen> createState() => _TripScreenState();
}

class _TripScreenState extends State<TripScreen> {
  final ApiService _apiService = ApiService();

  List<dynamic> _stops = [];
  int _completedStops = 0;
  int _totalStops = 0;
  bool _isLoading = true;
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _loadTasks();
    debugPrint('[TripScreen] tripId received: ${widget.tripId}');// For debugging: Ensure tripId is correct
    // Poll every 30 seconds
    _pollingTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _loadTasks(),
    );
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadTasks() async {
    try {
      final tasks = await _apiService.getTasks(widget.tripId);
      setState(() {
        _stops = tasks ?? [];
        _totalStops = _stops.length;
        _completedStops = _stops
            .where((t) => t['status'] == 'delivered')
            .length;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('loadTasks error: $e');
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Column(
          children: [
            const Text(
              'Optimised Sequence',
              style: TextStyle(
                color: Colors.black,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            Text(
              '${_totalStops - _completedStops} stops remaining',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.warning_amber, color: Colors.orange),
            onPressed: () {
              Navigator.pushNamed(
                context,
                '/emergency',
                arguments: widget.tripId,
              );
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Progress HUD
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 12,
                  ),
                  color: Colors.white,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Today\'s Progress',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFF8C42),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '$_completedStops/$_totalStops Completed',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Stop list
                Expanded(
                  child: _stops.isEmpty
                      ? const Center(child: Text('No stops found'))
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _stops.length,
                          itemBuilder: (context, index) {
                            final stop = _stops[index];
                            final isCompleted = stop['status'] == 'delivered';
                            final sequence =
                                stop['sequence_order'] ?? index + 1;
                            final recipientName =
                                stop['package']?['recipient_name'] ?? '';
                            final address =
                                stop['package']?['delivery_address'] ?? '';
                            final cod = stop['package']?['cod_amount'] ?? 0;

                            return GestureDetector(
                              onTap: () {
                                Navigator.pushNamed(
                                  context,
                                  '/stop-detail',
                                  arguments: stop['id'],
                                );
                              },
                              child: Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: isCompleted
                                        ? Colors.green.withOpacity(0.3)
                                        : Colors.grey.withOpacity(0.2),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    // Sequence number
                                    Container(
                                      width: 32,
                                      height: 32,
                                      decoration: BoxDecoration(
                                        color: isCompleted
                                            ? Colors.green
                                            : const Color(0xFFFF8C42),
                                        shape: BoxShape.circle,
                                      ),
                                      child: Center(
                                        child: isCompleted
                                            ? const Icon(
                                                Icons.check,
                                                color: Colors.white,
                                                size: 16,
                                              )
                                            : Text(
                                                '$sequence',
                                                style: const TextStyle(
                                                  color: Colors.white,
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 14,
                                                ),
                                              ),
                                      ),
                                    ),
                                    const SizedBox(width: 12),

                                    // Stop details
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            recipientName,
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 14,
                                              color: Colors.black,
                                            ),
                                          ),
                                          const SizedBox(height: 2),
                                          Text(
                                            address,
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),

                                    // COD
                                    Text(
                                      'Rs. $cod',
                                      style: const TextStyle(
                                        fontSize: 11,
                                        color: Colors.grey,
                                      ),
                                    ),
                                  ],
                                ),
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
