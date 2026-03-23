import 'package:flutter/material.dart';

class DeliveryStop {
  final String id;
  final int sequence;
  final String recipientName;
  final String address;
  final String eta;
  final double codAmount;
  final bool isCompleted;

  const DeliveryStop({
    required this.id,
    required this.sequence,
    required this.recipientName,
    required this.address,
    required this.eta,
    required this.codAmount,
    required this.isCompleted,
  });
}

// TODO: Replace with GET /api/v1/tasks?trip_id={id} — poll every 30s
const List<DeliveryStop> MOCK_STOPS = [
  DeliveryStop(
    id: '1',
    sequence: 1,
    recipientName: 'Ravindu Perera',
    address: '120/6 Colombo 03',
    eta: '10:46 AM',
    codAmount: 4500,
    isCompleted: true,
  ),
  DeliveryStop(
    id: '2',
    sequence: 2,
    recipientName: 'Saman Thirimanna',
    address: '130/21 Colombo 03',
    eta: '11:03 AM',
    codAmount: 3200,
    isCompleted: false,
  ),
  DeliveryStop(
    id: '3',
    sequence: 3,
    recipientName: 'HCM Holdings',
    address: '10/3 Colombo 03',
    eta: '11:28 AM',
    codAmount: 8900,
    isCompleted: false,
  ),
  DeliveryStop(
    id: '4',
    sequence: 4,
    recipientName: 'Nimal Perera',
    address: '45/2 Colombo 05',
    eta: '11:45 AM',
    codAmount: 1500,
    isCompleted: false,
  ),
  DeliveryStop(
    id: '5',
    sequence: 5,
    recipientName: 'Kamala Silva',
    address: '78/1 Colombo 07',
    eta: '12:10 PM',
    codAmount: 6700,
    isCompleted: false,
  ),
];

class TripScreen extends StatefulWidget {
  final String tripId;
  const TripScreen({super.key, required this.tripId});

  @override
  State<TripScreen> createState() => _TripScreenState();
}

class _TripScreenState extends State<TripScreen> {
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
            const Text(
              '29 stops remaining',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.warning_amber, color: Colors.orange),
            onPressed: () {
              Navigator.pushNamed(context, '/emergency');
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Progress HUD
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
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
                  child: const Text(
                    '1/5 Completed',
                    style: TextStyle(
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
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: MOCK_STOPS.length,
              itemBuilder: (context, index) {
                final stop = MOCK_STOPS[index];
                return GestureDetector(
                  onTap: () {
                    Navigator.pushNamed(context, '/stop-detail', arguments: stop.id);
                  },
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: stop.isCompleted
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
                            color: stop.isCompleted
                                ? Colors.green
                                : const Color(0xFFFF8C42),
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: stop.isCompleted
                                ? const Icon(
                                    Icons.check,
                                    color: Colors.white,
                                    size: 16,
                                  )
                                : Text(
                                    '${stop.sequence}',
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
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                stop.recipientName,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                  color: Colors.black,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                stop.address,
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey,
                                ),
                              ),
                            ],
                          ),
                        ),

                        // ETA
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              stop.eta,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                                color: Color(0xFFFF8C42),
                              ),
                            ),
                            Text(
                              'Rs. ${stop.codAmount.toStringAsFixed(0)}',
                              style: const TextStyle(
                                fontSize: 11,
                                color: Colors.grey,
                              ),
                            ),
                          ],
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
