"use client"
import { useRouter } from "next/navigation"
import { PACKAGES } from "./data"
import styles from "./page.module.css"

{/* Functions to format status text and get corresponding colors for different package statuses */}
function formatStatus(status: string) {
  return status.replace(/_/g, " ")
}

{/* Function to return color codes based on package status for visual representation in the UI */}
function getStatusColor(status: string) {
  switch (status) {
    case "TO_BE_DELIVERED": return "#10B981"
    case "DELIVERED": return "#2563EB"
    case "ASSIGNED": return "#F59E0B"
    case "ONGOING": return "#3B82F6"
    case "COMPLETED": return "#16A34A"
    case "FAILED": return "#EF4444"
    default: return "#6B7280"
  }
}

export default function PackagesPage() {
  {/*created a contant router to enable navigation to the add package page when the "Add New Package" button is clicked*/}
  const router = useRouter()
  
  return (
    <div className={styles.container}>{/*Main container that has the syling and formate of the page content*/}

      <div className={styles.header}>{/*Header section of the page that contains the title and the add button*/}
        <h1 className={styles.heading}>Packages</h1>
        <button className={styles.addButton} onClick={() => router.push("/packages/add")}>{/*Button to navigate to the add package page when clicked*/}
          + Add New Package
        </button>
      </div>

      <div className={styles.tableCard}>{/*This container holds the table that displays the list of packages with their details and their stlying*/}
        <table className={styles.table}>
          <thead>
            <tr className={styles.headerRow}>
              <th className={styles.thId}>Package ID</th>
              <th className={styles.thStatus}>Status</th>
              <th className={styles.thLocation}>Location</th>
              <th className={styles.thPhone}>Phone Number</th>
              <th className={styles.thAddress}>Address</th>
            </tr>
          </thead>
          <tbody>
            {/*Mapping through the PACKAGES array to create a table row for each package, displaying its details such as ID, status, location, phone number, and address. The status is formatted and colored based on its value for better visual distinction.*/}
            {PACKAGES.map((pkg) => (
              <tr key={pkg.id} className={styles.row}>
                <td className={styles.tdId}>#{pkg.id}</td>
                <td className={styles.tdStatus}>
                  <span style={{ color: getStatusColor(pkg.status), fontWeight: 600 }}>
                    {formatStatus(pkg.status)}
                  </span>{/*The status text is formatted to replace underscores with spaces and colored according to its value for better visual representation.*/}
                </td>
                <td className={styles.tdLocation}>
                  <img
                    src={pkg.location === "verified" ? "/Icons/Location_Available.svg" : "/Icons/Location_Unavailable.svg"}
                    alt={pkg.location}
                    className={styles.locationIcon}
                  />{/*An icon is displayed to indicate the location status of the package, showing a different icon for verified and unverified locations.*/}
                </td>
                <td className={styles.tdPhone}>{pkg.phone}</td>
                <td className={styles.tdAddress}>{pkg.address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  )
}