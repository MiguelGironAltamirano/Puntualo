/**
 * Pruebas de render de componentes de paginación.
 *
 * Nivel:   Unitaria (componente)
 * Tipo:    Funcional
 * Técnica: Caja Blanca (estados del componente)
 * Bajo prueba: components/pagination/Pagination.tsx
 *
 * Verifica que los componentes clave renderizan y que los estados de habilitación
 * y los callbacks responden a la interacción del usuario. Trazable a PRUEBAS.md
 * (Componentes frontend — render).
 */
import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { Pagination, ResultsInfo } from './Pagination';

describe('Pagination', () => {
  it('renderiza el indicador "Page X of Y"', () => {
    const { container } = render(
      <Pagination
        currentPage={2}
        totalPages={5}
        hasNext
        hasPrev
        onPageChange={() => {}}
      />,
    );

    // "Page 2 of 5" está repartido en varios spans; validamos el texto normalizado.
    expect(container).toHaveTextContent('Page 2 of 5');
  });

  it('deshabilita "anterior/primera" en la primera página', () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={3}
        hasNext
        hasPrev={false}
        onPageChange={() => {}}
      />,
    );

    expect(screen.getByLabelText('Go to first page')).toBeDisabled();
    expect(screen.getByLabelText('Go to previous page')).toBeDisabled();
  });

  it('invoca onPageChange con el número de página al hacer click', async () => {
    const user = userEvent.setup();
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={1}
        totalPages={3}
        hasNext
        hasPrev={false}
        onPageChange={onPageChange}
      />,
    );

    await user.click(screen.getByRole('button', { name: '3' }));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });
});

describe('ResultsInfo', () => {
  it('calcula el rango de resultados mostrado', () => {
    render(<ResultsInfo total={45} pageSize={20} currentPage={2} />);
    // Página 2 de 20 por página sobre 45 -> "Showing 21 to 40 of 45".
    expect(screen.getByText('21')).toBeInTheDocument();
    expect(screen.getByText('40')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
  });

  it('no renderiza nada cuando no hay datos', () => {
    const { container } = render(
      <ResultsInfo total={0} pageSize={20} currentPage={1} hasData={false} />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
