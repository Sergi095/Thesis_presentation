// Arrange the original slide nodes without replacing scientific text or assets.
function group(className, children) {
  const element = document.createElement('div');
  element.className = className;
  element.append(...children);
  return element;
}

const labels = {
  '2Dfast.gif': '2D simulation',
  'pybulletFast.gif': 'PyBullet simulation',
  'p_vectors.png': 'DM and ADM proximal control vectors',
  'predator_prey_distance_speed_up.gif': 'Predator distance modulation',
  'predator_prey_repulsion_fast2.gif': 'Prey escape response',
  'kappaPREDSdist.png': 'Repulsion strength versus predator distance',
  'PADM_fast.gif': 'Attractive distance modulation (ADM)',
  'PDM_fast.gif': 'Distance modulation (DM)',
};

export function arrangeSlide(root, index) {
  root.dataset.slide = index;
  root.querySelectorAll('img').forEach(img => {
    const name = img.getAttribute('src').split('/').pop();
    if (!labels[name]) return;
    const figure = document.createElement('figure');
    figure.className = 'slide-figure';
    const caption = document.createElement('figcaption');
    caption.textContent = labels[name];
    img.alt = labels[name];
    img.loading = 'eager';
    img.replaceWith(figure);
    figure.append(img, caption);
  });
  const nodes = [...root.children];
  if (index === 0) {
    nodes[0].className = 'intro-layout';
    nodes[0].children[1].className = 'figure-pair';
    nodes[1].className = 'intro-links';
  } else if (index === 3) {
    root.replaceChildren(group('text-figure-layout', [
      group('slide-copy', nodes.slice(0, 4)), nodes[4],
    ]), nodes[5]);
  } else if (index === 4) {
    root.replaceChildren(group('text-figure-layout', [
      group('slide-copy', nodes.filter((_, i) => i !== 3)), nodes[3],
    ]));
  } else if (index === 5) {
    const figures = [...nodes[5].children];
    root.replaceChildren(
      group('text-figure-layout', [group('slide-copy', nodes.slice(0, 5)), figures[0]]),
      group('text-figure-layout', [group('slide-copy', nodes.slice(6)), figures[1]]),
    );
  } else if (index === 6) {
    nodes[0].className = 'setup-layout';
  } else if (index === 10) {
    nodes[1].className = 'figure-pair';
  }
  root.querySelectorAll('iframe').forEach(frame => {
    frame.parentElement.classList.add('chart-panel');
    // Keep full-width plots legible; their original height is deliberate.
    frame.loading = 'eager';
  });
}
