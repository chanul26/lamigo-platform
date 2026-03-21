'use client';

import { User, Wallet, Zap } from 'lucide-react';
import Avatar from '@/components/Avatar';
import { useState } from 'react';
import SettlePaymentModal from '@/components/SettlePaymentModel';


{/* interface to define to get the data of the driver
  settlement from the database
  */ }
interface driverSettlement {
  id: string;
  driver_id: string;
  driver_name: string;
  total_pending: number;
}

{/* Mock data to test the table layout and 
  functionality before integrating with
  the backend API(Place holder for API endpoint) 
  */ }
const MOCK_SETTLEMENTS: driverSettlement[] = [
  { id: 'f1225531-a94d-48ac-958f-d94622015b64', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl2', driver_name: 'Saman Kumara',        total_pending: 18500 },
  { id: 'f1225531-a94d-48ac-958f-d94622015b65', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl3', driver_name: 'Nimal Perera',        total_pending: 4200  },
  { id: 'f1225531-a94d-48ac-958f-d94622015b66', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl4', driver_name: 'Kasun Jayasuriya',    total_pending: 12150 },
  { id: 'f1225531-a94d-48ac-958f-d94622015b67', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl5', driver_name: 'Amal Silva',          total_pending: 850   },
  { id: 'f1225531-a94d-48ac-958f-d94622015b68', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl6', driver_name: 'Ruwan Hettiarachchi', total_pending: 5600  },
  { id: 'f1225531-a94d-48ac-958f-d94622015b69', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl7', driver_name: 'Sunil Tennakoon',     total_pending: 0     },
];


export default function SettlementsPage() {

  const [settlements, setSettlements] = useState<driverSettlement[]>(MOCK_SETTLEMENTS);
  const [selected, setSelected] = useState<driverSettlement | null>(null);

  // Called after confirmed payment — resets driver's balance to 0
  function handlePaymentSuccess(settlementId: string) {
    setSettlements((prev) =>
      prev.map((s) => (s.id === settlementId ? { ...s, total_pending: 0 } : s))
    );
    setSelected(null);
  }


  return (
    <div className="p-8">{/* divison of the padge body content */}
      
      {/* Heading of the page */}
      <h1 className="text-3xl font-bold text-white mb-6">
        Settlements
      </h1>

      
      {/* Table container */}
      <div className="bg-[#1E1E1E] rounded-xl border border-[#2E2E2E] overflow-hidden">
        
        {/* Table start here */}
        <table className="w-full text-sm">
          <thead className="border-b border-[#2E2E2E]">

            {/*Row contain the table heading */}
            <tr className="border-b border-[#2E2E2E]">
            
              <th className="text-left px-6 py-4 text-[#A1A1A1] font-laerge ">
                <User size={20} />
                Driver
              </th>

              <th className="text-left px-6 py-4 text-[#A1A1A1] font-laerge">
                <Wallet size={20} />
                Total to be paid
              </th>
              
              <th className="text-left px-6 py-4 text-[#A1A1A1] font-laerge">
                <Zap size={20} />
                Action
              </th>

            </tr>

          </thead>

          <tbody>
            {settlements.map((s, i) => {

              {/* check whther the curent settlement is the last */}
              const isLast = i == settlements.length - 1;

              

              {/* chekc whther the current settelment total pending is above 0 */}
              const canPay = s.total_pending > 0;
              return (
                <tr
                  key = {s.id}
                  className = {`hover:bg-[#252525] transition-colors ${!isLast ? 'border-b border-[#2E2E2E]' : ''}`}
                >

                  {/*Driver column datas */}
                  <td className='px-6 py-4'>
                    <div className="flex items-center gap-3">
                      <Avatar name={s.driver_name} />
                      <div>
                        <p className="font-medium text-white">{s.driver_name}</p>
                        <p className="text-xs text-[#6B7280] mt-0.5">{s.driver_id.substring(0, 8)}</p>
                      </div>
                    </div>
                  </td>


                  {/* Column consist the payment data */}
                  <td className="px-6 py-4">
                    <span className="font-semibold text-white">
                      LKR {s.total_pending.toLocaleString()}
                    </span>
                  </td>

                  
                  {/* Column consist of button which navigate to payment related action */}
                  <td className="px-6 py-4">
                    <button
                      onClick={() => canPay && setSelected(s)}
                      disabled= {!canPay}
                      className={`px-5 py-2 text-sm font-semibold rounded-lg transition-colors ${canPay
                          ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                          : 'bg-[#252525] text-[#6B7280] cursor-not-allowed'
                        }`}

                    >
                      Pay
                    </button>
                  </td>

                </tr>
              );
            })}
          </tbody>
        
        
        </table>
      </div>


      {/* Text that link to Tab containing the past payment history */}
      <div className='mt-4'>

        <a href = "/settlements/history"
          className="w-full flex items-center justify-center py-3 text-sm font-medium rounded-lg border border-blue-600 text-blue-500 hover:bg-blue-600/10 transition-colors"
        >
          View Past Payment History
        </a>
      </div>

      {/* Settle Payment Modal */}
      {selected && (
        <SettlePaymentModal
          settlement={selected}
          onSuccess={handlePaymentSuccess}
          onClose={() => setSelected(null)}
        />
      )}

    </div>
  );
}