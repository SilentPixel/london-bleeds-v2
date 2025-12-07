export default function ContextPanel({ npcs, items, exits }: any) {
  return (
    <aside className="border-l pl-4 w-64 space-y-4 hidden md:block">
      <section>
        <h4 className="font-serif text-accent">Who's here</h4>
        <ul>{npcs?.map((n: any) => <li key={n}>{n}</li>)}</ul>
      </section>
      <section>
        <h4 className="font-serif text-accent">You see</h4>
        <ul>{items?.map((i: any) => <li key={i}>{i}</li>)}</ul>
      </section>
      <section>
        <h4 className="font-serif text-accent">Exits</h4>
        <ul>{exits?.map((e: any) => <li key={e}>{e}</li>)}</ul>
      </section>
    </aside>
  );
}

