import styles from "./page.module.css"

export default function AddPackagePage() {
  return (
    <div className={styles.container}>{/*Main container that has the syling and formate of the page content*/}

      <h1 className={styles.heading}>Add New Package</h1>

      <div className={styles.tabContainer}>{/*Tab container that holds the buttons to switch between manual entry and bulk upload for adding new packages, with styling to indicate the active tab.*/}
        <button className={styles.tabActive}>Manual Entry</button>
        <button className={styles.tabInactive}>Bulk Upload</button>
      </div>

      <div className={styles.formCard}>{/*Form card that contains the form fields for adding a new package, with styling for layout and spacing*/}

        <div className={styles.formGroup}>{/*Form group for the package number input field, with a label and an input box styled for user input*/}
          <label className={styles.label}>Package Number</label>
          <input className={styles.input} placeholder="e.g. PKG-2024-00123" />
        </div>

        <div className={styles.twoColumns}>{/*Container that holds two form groups side by side for receiver name and phone number, with styling to create a two-column layout*/}
          <div>
            <label className={styles.label}>Receiver Name</label>
            <input className={styles.input} placeholder="Saman Perera" />
          </div>
          <div>
            <label className={styles.label}>Phone Number</label>
            <input className={styles.input} placeholder="07x-xxx-xxxx" />
          </div>
        </div>

    <div className={styles.formGroup}>{/*Form group for the address input field, with a label and an input box styled for user input*/}
          <label className={styles.label}>Address</label>
          <input className={styles.input} placeholder="House No, Street Name" />
        </div>

        <div className={styles.twoColumns}>{/*Container that holds two form groups side by side for city/area and COD amount, with styling to create a two-column layout*/}
          <div>
            <label className={styles.label}>City/Area</label>
            <input className={styles.input} />
          </div>
          <div>
            <label className={styles.label}>COD Amount (LKR)</label>
            <input className={styles.input} placeholder="0.00" />
          </div>
        </div>

        <div className={styles.formGroup}>{/*Form group for the note/description input field, with a label and an input box styled for user input*/}
          <label className={styles.label}>Note / Description</label>
          <input className={styles.input} placeholder="e.g. Fragile" />
        </div>

        <p className={styles.helperText}>Package will be added to inventory and assigned to a driver.</p>

        <div className={styles.buttonRow}>{/*Container that holds the action buttons for canceling or submitting the form, with styling for layout and spacing*/}
          <button className={styles.cancelButton}>Cancel</button>
          <button className={styles.submitButton}>Add to Inventory</button>
        </div>

      </div>
    </div>
  )
}