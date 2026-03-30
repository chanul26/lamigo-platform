import 'package:flutter/material.dart';
import 'package:flutter_phone_direct_caller/flutter_phone_direct_caller.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../services/api_service.dart';

class StopDetailScreen extends StatefulWidget {
  final String stopId;
  const StopDetailScreen({super.key, required this.stopId});

  @override
  State<StopDetailScreen> createState() => _StopDetailScreenState();
}

class _StopDetailScreenState extends State<StopDetailScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _notesController = TextEditingController();

  // State variables
  String _recipientName = '';
  String _phone = '';
  String _address = '';
  double? _gpsLat;
  double? _gpsLng;
  double _codAmount = 0;
  String _customerInstructions = '';
  bool _isLoading = true;
  bool _isUpdating = false;

  double? _toNullableDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  double _toDouble(dynamic value) => _toNullableDouble(value) ?? 0.0;

  @override
  void initState() {
    super.initState();
    debugPrint('[StopDetail] stopId received: ${widget.stopId}');
    _loadTaskDetail();
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _loadTaskDetail() async {
    try {
      debugPrint('[StopDetail] Loading task: ${widget.stopId}');
      final task = await _apiService.getTask(widget.stopId);
      debugPrint('[StopDetail] task response: $task');
      if (!mounted) return;

      if (task == null) {
        setState(() => _isLoading = false);
        return;
      }

      final pkg = (task['package'] as Map?)?.cast<String, dynamic>();

      setState(() {
        _recipientName = pkg?['recipient_name'] ?? '';
        _phone = pkg?['recipient_phone'] ?? '';
        _address = pkg?['address'] ?? '';
        _codAmount = _toDouble(pkg?['cod_amount']);
        _gpsLat = _toNullableDouble(pkg?['gps_lat']);
        _gpsLng = _toNullableDouble(pkg?['gps_lng']);

        // Not currently part of TaskResponse schema; keep if backend sends it.
        _customerInstructions =
            task['task_instructions']?['instructions'] ?? '';

        _isLoading = false;
      });
    } catch (e) {
      debugPrint('loadTaskDetail error: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _updateTaskStatus(
    String status, {
    String? failureType,
  }) async {
    setState(() => _isUpdating = true);
    try {
      final result = await _apiService.updateTask(
        widget.stopId,
        status,
        failureType: failureType,
        // Swagger: failure_note is part of TaskUpdate for failed tasks.
        failureNote: failureType == null ? null : _notesController.text,
      );
      if (result != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Status updated to $status'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      debugPrint('updateTask error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
    if (mounted) setState(() => _isUpdating = false);
  }

  Future<void> _openGoogleMaps() async {
    final lat = _gpsLat;
    final lng = _gpsLng;
    if (lat == null || lng == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Destination coordinates missing')),
      );
      return;
    }

    final url =
        'https://www.google.com/maps/dir/?api=1&destination=${lat.toStringAsFixed(6)},${lng.toStringAsFixed(6)}';
    final uri = Uri.parse(url);

    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }

  void _showFailureReasonSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Select Failure Reason',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ...const <Map<String, String>>[
              {'type': 'NOT_HOME', 'label': 'NOT HOME'},
              {'type': 'UNREACHABLE', 'label': 'UNREACHABLE'},
              {'type': 'RECIPIENT_REJECTED', 'label': 'RECIPIENT REJECTED'},
              {'type': 'CANCELLED_BY_RECIPIENT', 'label': 'CANCELLED BY RECIPIENT'},
              {'type': 'CANCELLED_BY_MANAGER', 'label': 'CANCELLED BY MANAGER'},
              {'type': 'CANCELLED_BY_DRIVER', 'label': 'CANCELLED BY DRIVER'},
            ].map(
              (reason) => ListTile(
                title: Text(reason['label'] ?? reason['type'] ?? ''),
                onTap: () {
                  Navigator.pop(context);
                  _updateTaskStatus('FAILED', failureType: reason['type']);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Stop Detail',
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Recipient Card
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFF3E0),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Recipient',
                            style: TextStyle(fontSize: 12, color: Colors.grey)),
                        const SizedBox(height: 4),
                        Text(_recipientName,
                            style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.black)),
                        const SizedBox(height: 4),
                        Text(_address,
                            style: const TextStyle(
                                fontSize: 14, color: Colors.grey)),
                        const SizedBox(height: 12),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFF8C42),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            'COD: Rs. ${_codAmount.toStringAsFixed(0)}',
                            style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Customer Instructions
                  if (_customerInstructions.isNotEmpty)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border:
                            Border.all(color: Colors.grey.withOpacity(0.2)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Customer Instructions',
                              style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.black)),
                          const SizedBox(height: 8),
                          Text(_customerInstructions,
                              style: const TextStyle(
                                  fontSize: 13, color: Colors.grey)),
                        ],
                      ),
                    ),
                  const SizedBox(height: 16),

                  // Navigate and Call buttons
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isUpdating ? null : _openGoogleMaps,
                          icon: const Icon(Icons.navigation,
                              color: Colors.white),
                          label: const Text('Navigate',
                              style: TextStyle(color: Colors.white)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.black,
                            padding:
                                const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: (_isUpdating || _phone.isEmpty)
                              ? null
                              : () async {
                                  await FlutterPhoneDirectCaller
                                      .callNumber(_phone);
                                },
                          icon: const Icon(Icons.call, color: Colors.white),
                          label: const Text('Call',
                              style: TextStyle(color: Colors.white)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            padding:
                                const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Driver Notes
                  const Text('Driver Notes',
                      style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: Colors.black)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _notesController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      hintText: 'Add notes about this delivery...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(
                            color: Colors.grey.withOpacity(0.3)),
                      ),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Delivery Action Buttons
                  Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _isUpdating
                              ? null
                              : () => _updateTaskStatus('COMPLETED'),
                          icon: const Icon(Icons.check_circle,
                              color: Colors.white),
                          label: const Text('Mark Delivered',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            padding:
                                const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _isUpdating
                              ? null
                              : _showFailureReasonSheet,
                          icon: const Icon(Icons.cancel, color: Colors.white),
                          label: const Text('Mark Failed',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            padding:
                                const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _isUpdating
                              ? null
                              : () => _updateTaskStatus('SCHEDULED'),
                          icon: const Icon(Icons.schedule,
                              color: Colors.white),
                          label: const Text('Reschedule',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.grey,
                            padding:
                                const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Confirm & Continue
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text('Confirm & Continue',
                          style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16)),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}