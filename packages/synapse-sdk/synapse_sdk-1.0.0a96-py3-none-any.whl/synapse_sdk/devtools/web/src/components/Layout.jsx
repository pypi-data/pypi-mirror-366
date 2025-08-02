import NavigationSidebar from "./NavigationSidebar";

export default function Layout(props) {
  return (
    <div class="flex h-full">
      <NavigationSidebar />
      <main class="flex-1 overflow-auto lg:ml-0">
        {props.children}
      </main>
    </div>
  );
}