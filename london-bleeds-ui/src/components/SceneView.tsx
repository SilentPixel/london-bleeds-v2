import ReactMarkdown from "react-markdown";
import DOMPurify from "dompurify";

export default function SceneView({ content }: { content: string }) {
  const safe = DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ["p", "strong", "em", "ul", "li", "blockquote", "h3"]
  });
  return (
    <article className="prose prose-lg max-w-[68ch] text-primary mb-6">
      <ReactMarkdown>{safe}</ReactMarkdown>
    </article>
  );
}

