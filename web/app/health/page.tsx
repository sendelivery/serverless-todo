import utilStyles from "@/styles/utilities.css";

export default function Page() {
  return (
    <h1 className={`${utilStyles.headingXl} ${utilStyles.centredText}`}>
      🎊 All systems <span className={utilStyles.highlightedText}>GO!</span> 🎊
    </h1>
  );
}
