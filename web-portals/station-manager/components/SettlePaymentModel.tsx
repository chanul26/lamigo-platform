'use client';

import { X } from 'lucide-react';
import { useState } from 'react';

interface DriverSettlement {
    id: number;
    driver_id: number;
    driver_name: string;
    total_pending: number;
}

interface Props {
    settlement: DriverSettlement;
    onSuccess: (settlementId: number) => void;
    onClose: () => void;
}

export default function SettlePaymentModal({ settlement, onSuccess, onClose }: Props) {


    const [paymentMethod, setPaymentMethod] = useState<'cash' | 'bank_transfer'>('cash');

    // Tracks the amount entered by the user
    const [amount, setAmount] = useState(settlement.total_pending);

    // Tracks loading state when confirm is clicked
    const [isLoading, setIsLoading] = useState(false);

    // TODO: Replace with useMutation → PATCH /api/v1/settlements/{id}/mark-paid
    // Body: { payment_method }
    async function handleConfirm() {
        setIsLoading(true);
        await new Promise((r) => setTimeout(r, 700)); // remove when wired to real API
        onSuccess(settlement.id);
        setIsLoading(false);
    }

    


    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60" onClick={onClose} />

            {/* Panel */}
            <div className="relative z-10 w-full max-w-lg mx-4 bg-[#1E1E1E] border border-[#2E2E2E] rounded-2xl shadow-2xl flex flex-col">

                {/* Header */}
                <div className="flex items-start justify-between px-6 pt-6 pb-5 border-b border-[#2E2E2E]">
                    <div>
                        <h2 className="text-lg font-bold text-white">Settle Payment</h2>
                        <p className="text-sm text-[#A1A1A1] mt-0.5">
                            Recording payment for driver{' '}
                            <span className="text-white font-medium">{settlement.driver_name}</span>
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-full text-[#6B7280] hover:bg-[#252525] transition-colors"
                        aria-label="Close"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Body */}
                <div className="px-6 py-5 space-y-5">

                    {/* Total Due Amount */}
                    <div className="bg-[#121212] rounded-lg p-4">
                        <p className="text-xs font-semibold uppercase tracking-widest text-[#6B7280] mb-2">
                            Total Due Amount
                        </p>
                        <p className="text-3xl font-bold text-white">
                            LKR {settlement.total_pending.toLocaleString()}
                        </p>
                    </div>

                    {/* Amount and Payment Method side by side */}
                    <div className="grid grid-cols-2 gap-4">

                        {/* Amount Paying Now */}
                        <div>
                            <label htmlFor="pay-amount" className="block text-sm font-semibold text-white mb-2">
                                Amount Paying Now
                            </label>
                            <input
                                id="pay-amount"
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                                className="w-full px-4 py-3 bg-[#121212] text-white text-base rounded-lg outline-none border border-[#2E2E2E] focus:border-blue-600 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                            />
                            <p className="text-xs text-[#6B7280] mt-1">Adjust for partial payments.</p>
                        </div>

                        {/* Payment Method */}
                        <button
                            onClick={() => setPaymentMethod('cash')}
                            className={`w-full py-2.5 text-sm font-medium rounded-lg border transition-colors ${paymentMethod === 'cash'
                                    ? 'bg-blue-600 border-blue-600 text-white'
                                    : 'bg-[#121212] border-[#2E2E2E] text-[#A1A1A1] hover:border-blue-600/50'
                                }`}
                        >
                            Cash Handover
                        </button>

                        <button
                            onClick={() => setPaymentMethod('bank_transfer')}
                            className={`w-full py-2.5 text-sm font-medium rounded-lg border transition-colors ${paymentMethod === 'bank_transfer'
                                    ? 'bg-blue-600 border-blue-600 text-white'
                                    : 'bg-[#121212] border-[#2E2E2E] text-[#A1A1A1] hover:border-blue-600/50'
                                }`}
                        >
                            Bank Transfer
                        </button>

                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-6 py-4 border-t border-[#2E2E2E]">
                    <button
                        onClick={onClose}
                        className="px-5 py-2.5 text-sm font-medium text-[#A1A1A1] hover:bg-[#252525] rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                    {/* TODO: wire to PATCH /api/v1/settlements/{id}/mark-paid when Heshadha delivers settlements.py */}
                    <button 
                        onClick={handleConfirm}
                        disabled={isLoading}
                        className="px-6 py-2.5 bg-blue-600 
                        hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors"
                    >
                        Confirm Payment
                    </button>
                </div>

            </div>
        </div>
    );
}