import styles from "./styles.css";

export type CheckboxWithLabelProps = {
  label: string;
};

export default function CheckboxWithLabel(props: CheckboxWithLabelProps) {
  return (
    <div>
      <label className={styles.container}>
        {props.label}
        <input
          type="checkbox"
          id={props.label}
          name={props.label}
          className={styles.checkbox}
        />
        <span className={styles.styledCheckbox}></span>
      </label>
    </div>
  );
}
