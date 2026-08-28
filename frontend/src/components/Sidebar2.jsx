import ProductCard from "./ProductCard";

function Sidebar2() {
    return (
        <aside className="sidebar">
            <div className="list">
                <ProductCard variant="large" />
                <ProductCard variant="large" />
            </div>
        </aside>
    );
}

export default Sidebar2;