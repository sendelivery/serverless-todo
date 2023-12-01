import type { ChangeEvent } from "react";
import styles from "./styles.css";

export type CheckboxWithLabelProps = {
  label: string;
  defaultChecked: boolean;
  setChecked: (value: boolean) => void;
};

export default function CheckboxWithLabel(props: CheckboxWithLabelProps) {
  const { label, defaultChecked, setChecked } = props;

  const handleCheck = (e: ChangeEvent<HTMLInputElement>) => {
    // No need to prevent the default function here,
    // we still want to retain normal checkbox behaviour
    setChecked(e.target.checked);
  };

  return (
    <div>
      <label className={styles.label}>
        {label}
        <input
          type="checkbox"
          id={label}
          name={label}
          className={styles.checkbox}
          defaultChecked={defaultChecked}
          onChange={handleCheck}
        />
        <span className={styles.styledCheckbox}></span>
      </label>
    </div>
  );
}
