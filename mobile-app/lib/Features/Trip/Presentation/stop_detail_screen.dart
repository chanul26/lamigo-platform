import 'package:flutter/material.dart';
import 'package:flutter_phone_direct_caller/flutter_phone_direct_caller.dart';

class StopDetail {
  final String id;
  final String recipientName;
  final String phone;
  final String address;
  final double codAmount;
  final String customerInstructions;
  final double gpsLat;
  final double gpsLng;

  const StopDetail({
    required this.id,
    required this.recipientName,
    required this.phone,
    required this.address,
    required this.codAmount,
    required this.customerInstructions,
    required this.gpsLat,
    required this.gpsLng,
  });
}

// TODO: Replace with GET /api/v1/tasks/{task_id}
const StopDetail MOCK_STOP = StopDetail(
  id: 'STOP-001',
  recipientName: 'Ravindu Perera',
  phone: '+94771234567',
  address: '120/6 Colombo 03',
  codAmount: 4500,
  customerInstructions:
      'Leave with the security guard at the main lobby desk. Collect money from security guard.',
  gpsLat: 6.9271,
  gpsLng: 79.8612,
);

class StopDetailScreen extends StatefulWidget {
  final String stopId;
  const StopDetailScreen({super.key, required this.stopId});

  @override
  State<StopDetailScreen> createState() => _StopDetailScreenState();
}

class _StopDetailScreenState extends State<StopDetailScreen> {
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
      body: SingleChildScrollView(
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
                  const Text(
                    'Recipient',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    MOCK_STOP.recipientName,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    MOCK_STOP.address,
                    style: const TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),

                  // COD Badge
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFF8C42),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'COD: Rs. ${MOCK_STOP.codAmount.toStringAsFixed(0)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Customer Instructions
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.withOpacity(0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Customer Instructions',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    MOCK_STOP.customerInstructions,
                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                ],
              ),
            ),
            // Action Buttons — Navigate and Call
            Row(
              children: [
                // Navigate button
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // TODO: Launch Google Maps when API key is configured
                      // url_launcher: https://www.google.com/maps/dir/?api=1&destination=${MOCK_STOP.gpsLat},${MOCK_STOP.gpsLng}
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                            'Navigation will be available when Google Maps is configured',
                          ),
                        ),
                      );
                    },
                    icon: const Icon(Icons.navigation, color: Colors.white),
                    label: const Text(
                      'Navigate',
                      style: TextStyle(color: Colors.white),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),

                // Call button
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed : () async{
                      // TODO: Replace MOCK_STOP.phone with actual phone number from GET /api/v1/tasks/{task_id}
                      await FlutterPhoneDirectCaller.callNumber(MOCK_STOP.phone);
                    },
                    icon: const Icon(Icons.call, color: Colors.white),
                    label: const Text(
                      'Call',
                      style: TextStyle(color: Colors.white),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            // Driver Notes
            const Text(
              'Driver Notes',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Add notes about this delivery...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.grey.withOpacity(0.3)),
                ),
                filled: true,
                fillColor: Colors.white,
              ),
              // TODO: PATCH /api/v1/tasks/{task_id} { driver_notes: text }
            ),
            const SizedBox(height: 24),

            // Delivery Action Buttons
            // TODO: Wire to PATCH /api/v1/tasks/{task_id}
            Column(
              children: [
                // Mark Delivered
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // TODO: PATCH /api/v1/tasks/{id} { status: 'delivered', actual_arrival_time: DateTime.now() }
                    },
                    icon: const Icon(Icons.check_circle, color: Colors.white),
                    label: const Text(
                      'Mark Delivered',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // Mark Failed
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // TODO: Show bottom sheet with failure reason
                      // PATCH /api/v1/tasks/{id} { status: 'failed', failure_reason: 'gate_locked|not_home|wrong_address|other' }
                    },
                    icon: const Icon(Icons.cancel, color: Colors.white),
                    label: const Text(
                      'Mark Failed',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // Reschedule
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      // TODO: PATCH /api/v1/tasks/{id} { status: 'rescheduled' }
                    },
                    icon: const Icon(Icons.schedule, color: Colors.white),
                    label: const Text(
                      'Reschedule',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),

            // Content coming next
            const SizedBox(height: 24),

            // Confirm & Continue
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  // TODO: Navigate back to trip screen after confirming
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Confirm & Continue',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
