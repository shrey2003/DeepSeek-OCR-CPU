"""Demo script to run CPU inference on all images in test_files/images."""

from pathlib import Path

from inference import process_image, process_image_with_metrics, PerformanceTracker


def main() -> None:
    images_dir = Path("test_files/images").expanduser().resolve()
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {images_dir}")

    output_dir = images_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("IMAGE PROCESSING DEMO")
    print("="*70)
    
    # Track metrics across all images
    tracker = PerformanceTracker()
    
    image_files = sorted([
        f for f in images_dir.glob("*")
        if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    ])
    
    if not image_files:
        print("No image files found in the specified directory")
        return
    
    print(f"Found {len(image_files)} image(s) to process\n")

    for image_path in image_files:
        print(f"Processing {image_path.name}...")
        result, metrics = process_image_with_metrics(str(image_path), output_dir=str(output_dir))
        
        # Track metrics
        tracker.metrics.append(metrics)
        
        # Print metrics for this image
        print(f"  ✓ Completed in {metrics.total_time:.2f}s")
        print(f"    Tokens generated: {metrics.tokens_generated}")
        print(f"    Throughput: {metrics.tokens_per_second:.2f} tokens/sec")
        print()

    # Print aggregate metrics if more than one image
    if len(image_files) > 1:
        print("="*70)
        aggregate = tracker.aggregate()
        print(aggregate)


if __name__ == "__main__":
    main()
