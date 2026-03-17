'use client';


import { ArrowBigLeft, Calendar, CreditCard, User, Wallet } from "lucide-react";
import Avatar from "@/components/Avatar";
import { useState } from "react";

interface PaymentRecord {
    id: number;
    driver_id: number;
    driver_name: string;
    amount_paid: number;
    payment_method: 'cash' | 'bank_transfer';
    date: string; // ISO format date string


}


// TODO: When backend is ready, this will automatically reflect payments
// made from the settlements page via GET /api/v1/settlements?driver_id={id}
// TODO: Replace with useQuery → GET /api/v1/settlements?driver_id={id} when Heshadha delivers settlements.py
const MOCK_PAYMENT_HISTORY: PaymentRecord[] = [
    { id: 1, driver_id: 1, driver_name: 'Saman Kumara', amount_paid: 12000, payment_method: 'cash', date: '2026-03-01' },
    { id: 2, driver_id: 2, driver_name: 'Nimal Perera', amount_paid: 8500, payment_method: 'bank_transfer', date: '2026-03-03' },
    { id: 3, driver_id: 3, driver_name: 'Kasun Jayasuriya', amount_paid: 15000, payment_method: 'cash', date: '2026-03-05' },
    { id: 4, driver_id: 4, driver_name: 'Amal Silva', amount_paid: 3200, payment_method: 'bank_transfer', date: '2026-03-07' },
    { id: 5, driver_id: 5, driver_name: 'Ruwan Hettiarachchi', amount_paid: 9800, payment_method: 'cash', date: '2026-03-10' },
    { id: 6, driver_id: 6, driver_name: 'Sunil Tennakoon', amount_paid: 6400, payment_method: 'bank_transfer', date: '2026-03-12' },
];






export default function PaymentHistoryPage() {

    const [filterDriver, setFilterDriver] = useState('');
    const [filterDate, setFilterDate] = useState('');

    const filtered = MOCK_PAYMENT_HISTORY.filter((p) => {
        const matchesDriver = p.driver_name.toLowerCase().includes(filterDriver.toLowerCase());
        const matchesDate = filterDate ? p.date === filterDate : true;
        return matchesDriver && matchesDate;
    });


    return (
        <div className="p-8">

            {/* Back link */}

            <a
                href="/settlements"
                className="flex items-center gap-2 text-sm text-[#A1A1A1] hover:text-white transition-colors mb-6"
            >
                <ArrowBigLeft size={18} />
                Back to Settlements
            </a>

            {/* Page title */}
            <h1 className="text-3xl font-bold text-white mb-6">Payment History</h1>
            

            {/* Filter bar */}
            <div className="flex gap-3 mb-4">

                <input
                    type="text"
                    placeholder="Search by driver name..."
                    value={filterDriver}
                    onChange={(e) => setFilterDriver(e.target.value)}
                    className="flex-1 px-4 py-2.5 bg-[#1E1E1E] text-white text-sm rounded-lg border border-[#2E2E2E] outline-none focus:border-blue-600 transition-colors placeholder:text-[#6B7280]"
                />

                <input
                    type="date"
                    value={filterDate}
                    onChange={(e) => setFilterDate(e.target.value)}
                    className="px-4 py-2.5 bg-[#1E1E1E] text-white text-sm rounded-lg border border-[#2E2E2E] outline-none focus:border-blue-600 transition-colors"
                />

            </div>

            {/* Table card will go here */}
            <div className="bg-[#1E1E1E] rounded-xl
       border border-[#2E2E2E] overflow-hidden">

                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-[#2E2E2E]">

                            <th className="text-left px-6 py-4 text-xs font-semibold
                     text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <Calendar size={14} />
                                    Date
                                </div>
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <User size={14} />
                                    Driver
                                </div>
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <Wallet size={14} />
                                    Amount Paid
                                </div>
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <CreditCard size={14} />
                                    Payment Method
                                </div>
                            </th>



                        </tr>
                    </thead>

                    <tbody>
                        {filtered.map((p, i) => {
                            const isLast = i === MOCK_PAYMENT_HISTORY.length - 1;

                            return (

                                <tr

                                    key={p.id}
                                    className={`hover:bg-[#252525] 
                                        transition-colors 
                                        ${!isLast ? 'border-b border-[#2E2E2E]' : ''}`}

                                >
                                    {/* Date column */}
                                    <td className="px-6 py-4 text-[#A1A1A1]">
                                        {p.date}
                                    </td>

                                    {/* Driver column */}
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <Avatar name={p.driver_name} size="md" />
                                            <div>
                                                <p className="font-medium text-white">{p.driver_name}</p>
                                                <p className="text-xs text-[#6B7280] mt-0.5">#DRV-00{p.driver_id}</p>
                                            </div>
                                        </div>
                                    </td>

                                    {/* Amount Paid column */}
                                    <td className="px-6 py-4">
                                        <span className="font-semibold text-green-400">
                                            + LKR {p.amount_paid.toLocaleString()}
                                        </span>
                                    </td>

                                    {/* Payment Method column */}
                                    <td className="px-6 py-4">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${p.payment_method === 'cash'
                                                ? 'bg-blue-600/20 text-blue-400'
                                                : 'bg-purple-600/20 text-purple-400'
                                            }`}>
                                            {p.payment_method === 'cash' ? 'Cash Handover' : 'Bank Transfer'}
                                        </span>
                                    </td>

                                </tr>

                            )
                        })}
                    </tbody>
                </table>

            </div>

        </div>
    );
}